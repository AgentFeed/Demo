from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.learning import default_model_path, train_from_dataset
else:
    from ..learning import default_model_path, train_from_dataset


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = ROOT / "training" / "demo_interactions.csv"
DEFAULT_USERS = ROOT / "training" / "demo_users.csv"
DEFAULT_ITEMS = ROOT / "training" / "demo_jobs.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Bharat Career Twin's learned job ranker")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="CSV, JSON, or JSONL interaction export")
    parser.add_argument("--users", default=str(DEFAULT_USERS), help="Optional user/profile catalog")
    parser.add_argument("--items", default=str(DEFAULT_ITEMS), help="Optional job/vacancy catalog")
    parser.add_argument("--output", default=str(default_model_path()), help="Output JSON model artifact")
    parser.add_argument("--epochs", type=int, default=300)
    args = parser.parse_args()
    result = train_from_dataset(args.dataset, args.output, users_path=args.users, items_path=args.items, epochs=args.epochs)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
