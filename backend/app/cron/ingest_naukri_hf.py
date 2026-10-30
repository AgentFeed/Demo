"""Ingest real Naukri.com job postings (HuggingFace JSONL export) into the jobs store.

Source dataset: muhammetakkurt/naukri-jobs-dataset (HuggingFace, CC-BY-NC-4.0),
collected from Naukri.com for Software Engineer and Data Scientist roles.
Record source, license, and date in the project report when using this data.

Usage:
    python -m app.cron.ingest_naukri_hf --file ../data/raw/naukri_swe.jsonl --limit 20000
    python -m app.cron.ingest_naukri_hf --all   # ingests every naukri_*.jsonl in ../data/raw
"""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.runtime import create_store
else:
    from ..runtime import create_store

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _clean_text(value: Any, limit: int = 1200) -> str:
    if not value:
        return ""
    text = html.unescape(_TAG_RE.sub(" ", str(value)))
    return _WS_RE.sub(" ", text).strip()[:limit]


def _parse_skills(value: Any, title: str) -> list[str]:
    raw = [part.strip() for part in str(value or "").split(",") if part.strip()]
    skills = [skill for skill in raw if 1 < len(skill) <= 40]
    return skills[:12] or [word for word in title.split() if len(word) > 3][:4]


def _parse_created(value: Any) -> str | None:
    # Naukri exports "2024-12-23 06:51:32"; the store requires timezone-aware ISO.
    if not value:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.isoformat()


def normalize_naukri_row(row: dict[str, Any]) -> dict[str, Any] | None:
    job_id = str(row.get("jobId") or row.get("groupId") or "").strip()
    title = _clean_text(row.get("title"), limit=140)
    if not job_id or not title:
        return None
    location = _clean_text(row.get("location"), limit=60)
    city = location.split(",")[0].strip() if location else "India"
    skills = _parse_skills(row.get("tagsAndSkills"), title)
    return {
        "freehire_id": f"naukri-{job_id}",
        "title": title,
        "company": _clean_text(row.get("companyName"), limit=120) or "Unknown company",
        "location": city,
        "location_state": "",
        "description": _clean_text(row.get("jobDescription")),
        "url": row.get("jdURL"),
        "board": "naukri",
        "provider": "naukri_hf",
        "posted_at": _parse_created(row.get("createdDate")),
        "skills": skills,
        "salary": _clean_text(row.get("salary"), limit=60) or "Not listed",
    }


def load_jsonl(path: str | Path, limit: int | None = None) -> list[dict[str, Any]]:
    source = Path(path)
    postings: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            normalized = normalize_naukri_row(row)
            if normalized:
                postings.append(normalized)
            if limit and len(postings) >= limit:
                break
    return postings


def ingest(path: str | Path, limit: int | None = None) -> dict[str, Any]:
    postings = load_jsonl(path, limit)
    inserted, updated = create_store().upsert_kaggle_jobs(postings)
    return {
        "file": str(path),
        "read": len(postings),
        "inserted": inserted,
        "updated": updated,
        "source": "naukri_hf",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Naukri JSONL job postings into the local jobs store")
    parser.add_argument("--file", help="Path to a naukri_*.jsonl export")
    parser.add_argument("--all", action="store_true", help="Ingest every naukri_*.jsonl under ../data/raw")
    parser.add_argument("--limit", type=int, default=20000, help="Max rows per file (most recent first)")
    args = parser.parse_args()

    if args.all:
        raw_dir = Path(__file__).resolve().parents[3] / "data" / "raw"
        files = sorted(raw_dir.glob("naukri_*.jsonl"))
        if not files:
            raise SystemExit(f"No naukri_*.jsonl files found under {raw_dir}")
        results = [ingest(path, args.limit) for path in files]
    elif args.file:
        results = [ingest(args.file, args.limit)]
    else:
        parser.error("Provide --file PATH or --all")
        return

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
