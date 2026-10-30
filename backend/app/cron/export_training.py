from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.runtime import create_store
else:
    from ..runtime import create_store


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def export(output_dir: str | Path, limit: int = 100000) -> dict[str, str | int]:
    output = Path(output_dir)
    store = create_store()
    users = []
    for user_id in ("demo_fresher", "demo_govt", "demo_founder"):
        try:
            user = store.get_user(user_id)
        except KeyError:
            continue
        users.append({
            "user_id": user["id"], "skills": json.dumps(user.get("skills") or []),
            "interests": json.dumps(user.get("interests") or []), "hates": json.dumps(user.get("hates") or []),
            "city": user.get("city") or "",
        })
    jobs = []
    for job in store.list_jobs():
        jobs.append({
            "item_id": job["id"], "title": job.get("title") or "", "skills": json.dumps(job.get("skills") or []),
            "location": job.get("location") or "", "type": "job", "likes": job.get("likes", 0),
            "saves": job.get("saves", 0), "fresh_hours": job.get("fresh_hours", 12),
            "description": job.get("description") or "",
        })
    events = []
    for row in store.list_impressions(limit=limit):
        events.append({
            "user_id": row["user_id"], "item_id": row["item_id"], "action": "impression",
            "timestamp": row["created_at"], "rank_position": row.get("rank_position", 0),
            "model_version": row.get("model_version", "rules-v1"),
        })
    for row in store.list_interactions(limit=limit):
        events.append({
            "user_id": row["user_id"], "item_id": row["item_id"], "action": row["action"],
            "timestamp": row["created_at"], "rank_position": "", "model_version": "",
        })
    events.sort(key=lambda row: row["timestamp"])
    _write_csv(output / "users.csv", users, ["user_id", "skills", "interests", "hates", "city"])
    _write_csv(output / "items.csv", jobs, ["item_id", "title", "skills", "location", "type", "likes", "saves", "fresh_hours", "description"])
    _write_csv(output / "interactions.csv", events, ["user_id", "item_id", "action", "timestamp", "rank_position", "model_version"])
    return {"output_dir": str(output), "users": len(users), "items": len(jobs), "events": len(events)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export local impressions and actions for ranker retraining")
    parser.add_argument("--output-dir", default="training/exported")
    parser.add_argument("--limit", type=int, default=100000)
    args = parser.parse_args()
    print(json.dumps(export(args.output_dir, args.limit), indent=2))


if __name__ == "__main__":
    main()
