from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.config import settings
    from app.integrations.freehire import load_configured_freehire
    from app.runtime import create_store
else:
    from ..config import settings
    from ..integrations.freehire import load_configured_freehire
    from ..runtime import create_store


INDIA_TOKENS = {
    "india", "remote", "mumbai", "delhi", "new delhi", "ncr", "bengaluru", "bangalore",
    "hyderabad", "secunderabad", "chennai", "pune", "kolkata", "ahmedabad", "jaipur",
    "lucknow", "nagpur", "indore", "bhopal", "chandigarh", "kochi", "coimbatore",
    "noida", "greater noida", "gurgaon", "gurugram", "vadodara", "surat", "visakhapatnam",
    "thane", "nashik", "faridabad", "ghaziabad", "mysuru", "mysore", "madurai",
    "maharashtra", "karnataka", "telangana", "tamil nadu", "uttar pradesh", "gujarat",
    "west bengal", "rajasthan", "madhya pradesh", "haryana", "punjab", "kerala",
    "andhra pradesh", "bihar", "odisha", "assam", "uttarakhand", "himachal", "goa",
}


def india_relevant(posting: dict[str, Any]) -> bool:
    """Bharat-facing feed policy: keep India-located and remote/global-remote roles."""
    location = str(posting.get("location") or "").lower()
    return any(token in location for token in INDIA_TOKENS)


def load_postings(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("postings") or payload.get("jobs") or []
    if not isinstance(payload, list):
        raise ValueError("Expected a JSON array or an object with postings/jobs")
    return [item for item in payload if isinstance(item, dict)]


def sync(path: str | Path | None = None, *, india_only: bool = True) -> tuple[int, int]:
    postings = load_postings(path) if path else load_configured_freehire()
    if india_only:
        postings = [posting for posting in postings if india_relevant(posting)]
    return create_store().upsert_freehire_jobs(postings)


def main() -> None:
    parser = argparse.ArgumentParser(description="Idempotently sync a freehire JSON export into the local jobs store")
    parser.add_argument("json_path", nargs="?", help="Optional path to a freehire export JSON file; otherwise use configured environment source")
    parser.add_argument("--all-locations", action="store_true", help="Do not filter to India-located/remote postings")
    args = parser.parse_args()
    inserted, updated = sync(args.json_path, india_only=not args.all_locations)
    print(json.dumps({"inserted": inserted, "updated": updated, "source": "freehire", "india_only": not args.all_locations}))


if __name__ == "__main__":
    main()
