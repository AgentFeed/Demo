"""Convert the Kaggle CareerBuilder Job Recommendation Challenge export.

Source: https://www.kaggle.com/c/job-recommendation (free Kaggle account,
accept the competition rules, download the data zip, unzip it into a folder).

Expected files in --data-dir:
- apps.tsv  (UserID, JobID, ApplicationDate)  -> apply interactions
- users.tsv (UserID, WindowID, Split, City, State, ApplicationDate, JobTitle)
- jobs.tsv  (JobID, WindowID, Title, Description, Requirements, City, State, ...)

Output (in --output-dir, default training/careerbuilder):
- users.csv, items.csv, interactions.csv in the train_ranker loader contract.

Then train on REAL interaction labels:

    python -m app.cron.train_ranker \
        --dataset training/careerbuilder/interactions.csv \
        --users training/careerbuilder/users.csv \
        --items training/careerbuilder/items.csv \
        --epochs 1500

Rows with missing keys or shifted columns (a known quirk of this export) are
skipped and counted. Applications whose user or job is missing from the
catalogs are dropped so the feature join stays complete.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z+#.]{2,}")


def _read_tsv(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = [name.strip() for name in next(reader)]
        width = len(header)
        for raw in reader:
            if len(raw) != width:
                continue  # malformed/shifted row, common in this export
            rows.append({key: (value or "").strip() for key, value in zip(header, raw)})
    return rows


def _skills_from_text(*texts: str, limit: int = 10) -> list[str]:
    tokens: list[str] = []
    for text in texts:
        tokens.extend(match.group(0).lower() for match in _TOKEN_RE.finditer(text or ""))
    seen: list[str] = []
    for token in tokens:
        if token not in seen:
            seen.append(token)
        if len(seen) >= limit:
            break
    return seen


def _iso(value: str) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            parsed = datetime.strptime(value, "%m/%d/%Y")
        except ValueError:
            return None
    return parsed.replace(tzinfo=timezone.utc).isoformat()


def convert(data_dir: Path, output_dir: Path) -> dict[str, Any]:
    apps_path = data_dir / "apps.tsv"
    users_path = data_dir / "users.tsv"
    jobs_path = data_dir / "jobs.tsv"
    for path in (apps_path, users_path, jobs_path):
        if not path.exists():
            raise SystemExit(f"Missing {path.name} in {data_dir}; unzip the Kaggle export there first.")

    users_raw = _read_tsv(users_path)
    jobs_raw = _read_tsv(jobs_path)
    apps_raw = _read_tsv(apps_path)

    users: dict[str, dict[str, Any]] = {}
    for row in users_raw:
        user_id = row.get("UserID")
        if not user_id:
            continue
        users[user_id] = {
            "user_id": user_id,
            "skills": "|".join(_skills_from_text(row.get("JobTitle", ""))),
            "interests": "|".join(_skills_from_text(row.get("JobTitle", ""), limit=5)),
            "hates": "",
            "city": row.get("City") or row.get("State") or "",
        }

    items: dict[str, dict[str, Any]] = {}
    for row in jobs_raw:
        job_id = row.get("JobID")
        if not job_id:
            continue
        items[job_id] = {
            "item_id": job_id,
            "title": (row.get("Title") or "Untitled role")[:140],
            "skills": "|".join(_skills_from_text(row.get("Requirements", ""), row.get("Title", ""))),
            "location": row.get("City") or row.get("State") or "",
            "type": "job",
            "likes": 0, "saves": 0, "fresh_hours": 24, "has_referral": 0, "social_score": 0.0,
            "description": (row.get("Description") or "")[:300],
        }

    interactions: list[dict[str, Any]] = []
    skipped = 0
    for row in apps_raw:
        user_id, job_id = row.get("UserID"), row.get("JobID")
        if not user_id or not job_id or user_id not in users or job_id not in items:
            skipped += 1
            continue
        stamp = _iso(row.get("ApplicationDate") or "") or datetime(2012, 1, 1, tzinfo=timezone.utc).isoformat()
        interactions.append({"user_id": user_id, "item_id": job_id, "action": "apply", "timestamp": stamp})
    interactions.sort(key=lambda row: row["timestamp"])

    # Apply counts from the earliest 80% become the popularity feature.
    cutoff = int(len(interactions) * 0.8)
    apply_counts: Counter[str] = Counter(row["item_id"] for row in interactions[:cutoff])
    for job_id, item in items.items():
        item["likes"] = apply_counts.get(job_id, 0)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "users.csv", ["user_id", "skills", "interests", "hates", "city"], users.values())
    _write_csv(output_dir / "items.csv", list(next(iter(items.values())).keys()), items.values())
    _write_csv(output_dir / "interactions.csv", ["user_id", "item_id", "action", "timestamp"], interactions)
    return {
        "users": len(users), "items": len(items), "interactions": len(interactions),
        "skipped_apps": skipped, "output_dir": str(output_dir),
        "source": "Kaggle CareerBuilder Job Recommendation Challenge",
        "note": "Real user-job application labels; skills are tokenised from job titles/requirements.",
    }


def _write_csv(path: Path, fieldnames: list[str], rows: Any) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Kaggle CareerBuilder TSV export to the loader contract")
    parser.add_argument("--data-dir", required=True, help="Folder containing apps.tsv, users.tsv, jobs.tsv")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else Path(__file__).resolve().parents[2] / "training" / "careerbuilder"
    print(json.dumps(convert(Path(args.data_dir), output_dir), indent=2))


if __name__ == "__main__":
    main()
