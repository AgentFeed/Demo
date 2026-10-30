"""Generate a simulated interaction dataset on top of the REAL ingested job catalog.

This is a transparent behavioral simulation, NOT real user data. Its purpose is
to exercise the training pipeline at realistic scale until an approved real
interaction dataset (e.g. Kaggle CareerBuilder Job Recommendation Challenge) is
converted with convert_careerbuilder.py. Label it as simulation in the report.

The simulator draws user skill profiles, cities, and hated skills from the
actual jobs table, so feature distributions match the live catalog. Action
probabilities follow the same signals the ranker learns (skill overlap, city
match, freshness), with impression rows logged for every exposure.

Usage:
    python -m app.cron.simulate_interactions --users 400 --events-per-user 50
    # writes training/simulated/{users,items,interactions}.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.runtime import create_store
else:
    from ..runtime import create_store

SKILL_VOCAB_SIZE = 120
CITY_VOCAB_SIZE = 25
START = datetime(2026, 8, 25)


def _weighted_sample(counter: Counter[str], count: int, rng: random.Random, exclude: set[str] | None = None) -> list[str]:
    pool = [(value, weight) for value, weight in counter.items() if value and (not exclude or value not in exclude)]
    picked: list[str] = []
    pool_local = list(pool)
    while pool_local and len(picked) < count:
        weights = [weight for _, weight in pool_local]
        choice = rng.choices([value for value, _ in pool_local], weights=weights, k=1)[0]
        picked.append(choice)
        pool_local = [(value, weight) for value, weight in pool_local if value != choice]
    return picked


ACTION_STRENGTH = {"impression": 0, "view": 1, "click": 2, "like": 3, "share": 4, "save": 5, "apply": 6, "referral": 7, "hide": 8}


def dedupe_strongest(interactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse each (user, item) pair to its strongest logged action.

    Pointwise rankers cannot distinguish two rows with identical features and
    conflicting labels (an exposure and a later apply), so the training export
    keeps one row per user-item pair: the strongest observed action. `hide`
    stays strongest because it is an explicit boundary, not just a weak signal.
    """
    best: dict[tuple[str, str], dict[str, Any]] = {}
    for row in interactions:
        key = (row["user_id"], row["item_id"])
        current = best.get(key)
        if current is None or ACTION_STRENGTH.get(row["action"], 0) > ACTION_STRENGTH.get(current["action"], 0):
            best[key] = row
    return sorted(best.values(), key=lambda row: row["timestamp"])


def simulate(jobs: list[dict[str, Any]], user_count: int, events_per_user: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    skill_counter: Counter[str] = Counter()
    city_counter: Counter[str] = Counter()
    by_skill: dict[str, list[int]] = {}
    for index, job in enumerate(jobs):
        for skill in job.get("skills") or []:
            key = skill.lower()
            skill_counter[key] += 1
            by_skill.setdefault(key, []).append(index)
        city = (job.get("location") or "").strip().lower()
        if city:
            city_counter[city] += 1

    top_skills = [skill for skill, _ in skill_counter.most_common(SKILL_VOCAB_SIZE)]
    top_cities = [city for city, _ in city_counter.most_common(CITY_VOCAB_SIZE)]
    city_weights = [city_counter[city] for city in top_cities]

    users: list[dict[str, Any]] = []
    interactions: list[dict[str, Any]] = []
    for user_index in range(user_count):
        user_id = f"sim_user_{user_index + 1:04d}"
        skills = _weighted_sample(Counter({skill: skill_counter[skill] for skill in top_skills}), rng.randint(3, 6), rng)
        city = rng.choices(top_cities, weights=city_weights, k=1)[0]
        hates = _weighted_sample(Counter({skill: skill_counter[skill] for skill in top_skills}), rng.randint(1, 2), rng, exclude=set(skills))
        user = {"user_id": user_id, "skills": skills, "interests": skills[:3], "hates": hates, "city": city}
        users.append(user)

        skill_set = {skill.lower() for skill in skills}
        targeted_pool = [by_skill.get(skill, []) for skill in skill_set]
        targeted_pool = [index for pool in targeted_pool for index in pool]
        cursor = START + timedelta(days=rng.uniform(0, 5))
        for _ in range(events_per_user):
            if targeted_pool and rng.random() < 0.65:
                job_index = rng.choice(targeted_pool)
            else:
                job_index = rng.randrange(len(jobs))
            job = jobs[job_index]
            job_skills = {str(skill).lower() for skill in job.get("skills") or []}
            overlap = len(skill_set & job_skills) / max(1, len(job_skills))
            same_city = 1.0 if (job.get("location") or "").strip().lower() == city else 0.0
            fresh_hours = job.get("fresh_hours")
            freshness = 2.718 ** (-(float(fresh_hours) if fresh_hours is not None else 48.0) / 72.0)
            item_id = job.get("id") or job.get("item_id")
            cursor = cursor + timedelta(hours=rng.uniform(1, 30))
            interactions.append({"user_id": user_id, "item_id": item_id, "action": "impression", "timestamp": cursor.isoformat()})
            strength = 0.55 * overlap + 0.2 * same_city + 0.25 * freshness
            hated = bool(job_skills & {hate.lower() for hate in hates})
            if hated and overlap < 0.2 and rng.random() < 0.5:
                action = "hide"
            elif rng.random() < 0.12 + 0.72 * strength:
                roll = rng.random()
                if roll < 0.45 * (1.0 - strength):
                    action = "view"
                elif roll < 0.75 - 0.3 * strength:
                    action = "click"
                elif roll < 0.9:
                    action = "save"
                else:
                    action = "apply"
            else:
                continue
            interactions.append({
                "user_id": user_id, "item_id": item_id, "action": action,
                "timestamp": (cursor + timedelta(minutes=rng.uniform(1, 90))).isoformat(),
            })

    items = []
    deduped = dedupe_strongest(interactions)
    like_counts: Counter[str] = Counter()
    save_counts: Counter[str] = Counter()
    for row in deduped:
        if row["action"] in {"view", "click", "like"}:
            like_counts[row["item_id"]] += 1
        elif row["action"] == "save":
            save_counts[row["item_id"]] += 1
    for job in jobs:
        item_id = job.get("id")
        items.append({
            "item_id": item_id, "title": job.get("title"), "skills": "|".join(job.get("skills") or []),
            "location": job.get("location"), "type": "job",
            "likes": like_counts.get(item_id, 0), "saves": save_counts.get(item_id, 0),
            "fresh_hours": round(float(job.get("fresh_hours") or 0), 1), "has_referral": 0, "social_score": 0.0,
            "description": (job.get("description") or "")[:300],
        })
    return {"users": users, "items": items, "interactions": deduped}


def write_outputs(data: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "users.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["user_id", "skills", "interests", "hates", "city"])
        writer.writeheader()
        for user in data["users"]:
            writer.writerow({**user, "skills": "|".join(user["skills"]), "interests": "|".join(user["interests"]), "hates": "|".join(user["hates"])})
    with (output_dir / "items.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data["items"][0].keys()))
        writer.writeheader()
        writer.writerows(data["items"])
    with (output_dir / "interactions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["user_id", "item_id", "action", "timestamp"])
        writer.writeheader()
        writer.writerows(data["interactions"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate interaction logs over the real ingested catalog")
    parser.add_argument("--users", type=int, default=400)
    parser.add_argument("--events-per-user", type=int, default=50)
    parser.add_argument("--jobs-limit", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    store = create_store()
    jobs = [job for job in store.list_jobs() if job.get("skills")][: args.jobs_limit]
    if len(jobs) < 50:
        raise SystemExit("Not enough jobs with skills in the store; ingest catalog data first.")

    data = simulate(jobs, args.users, args.events_per_user, args.seed)
    output_dir = Path(args.output_dir) if args.output_dir else Path(__file__).resolve().parents[2] / "training" / "simulated"
    write_outputs(data, output_dir)
    actions = Counter(row["action"] for row in data["interactions"])
    print(json.dumps({
        "output_dir": str(output_dir), "jobs_used": len(jobs),
        "users": len(data["users"]), "interactions": len(data["interactions"]), "action_mix": dict(actions),
        "note": "simulated behaviour over the real catalog; replace with CareerBuilder export for real labels",
    }, indent=2))


if __name__ == "__main__":
    main()
