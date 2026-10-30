"""Keep the job catalog fresh automatically.

Every cycle (default 6 hours):
1. Sync live postings from freehire (India/remote filter on).
2. Optionally export local impressions/interactions and retrain the ranker
   (only when --retrain is passed and enough new events exist).

Run modes:
    python -m app.cron.auto_refresh --once        # single cycle, for Task Scheduler
    python -m app.cron.auto_refresh               # loop forever, every 6h
    python -m app.cron.auto_refresh --retrain     # loop + retrain when data allows

Windows Task Scheduler (background, no window):
    schtasks /Create /TN "BharatCareerTwinRefresh" /SC HOURLY /MO 6 ^
      /TR "py -3.12 -m app.cron.auto_refresh --once" ^
      /F && schtasks /Run /TN "BharatCareerTwinRefresh"
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.cron.sync_freehire import sync
else:
    from ..cron.sync_freehire import sync

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "auto_refresh.log"
MIN_EVENTS_FOR_RETRAIN = 50


def _log(event: dict) -> None:
    line = json.dumps({"at": datetime.now(timezone.utc).isoformat(), **event})
    print(line, flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass


def _interaction_count() -> int:
    try:
        if __package__ in {None, ""}:
            from app.runtime import create_store
        else:
            from ..runtime import create_store
        store = create_store()
        interactions = store.list_interactions(limit=1_000_000) if hasattr(store, "list_interactions") else []
        return len(interactions)
    except Exception as exc:  # pragma: no cover - defensive
        _log({"event": "interaction_count_failed", "error": str(exc)})
        return 0


def run_cycle(*, retrain: bool) -> None:
    try:
        inserted, updated = sync(india_only=True)
        _log({"event": "freehire_sync", "inserted": inserted, "updated": updated})
    except Exception as exc:
        _log({"event": "freehire_sync_failed", "error": str(exc)})

    if not retrain:
        return
    events = _interaction_count()
    if events < MIN_EVENTS_FOR_RETRAIN:
        _log({"event": "retrain_skipped", "interactions": events, "minimum": MIN_EVENTS_FOR_RETRAIN})
        return
    try:
        if __package__ in {None, ""}:
            from app.cron.export_training import export
            from app.learning import default_model_path, train_from_dataset
        else:
            from ..cron.export_training import export
            from ..learning import default_model_path, train_from_dataset
        export_dir = Path(__file__).resolve().parents[2] / "training" / "exported"
        export(export_dir)
        result = train_from_dataset(
            export_dir / "interactions.csv",
            default_model_path(),
            users_path=export_dir / "users.csv",
            items_path=export_dir / "items.csv",
        )
        _log({"event": "retrain", "trained": result.get("trained_examples"), "metrics": result.get("metrics")})
    except Exception as exc:
        _log({"event": "retrain_failed", "error": str(exc)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Periodically refresh live jobs and optionally retrain")
    parser.add_argument("--interval-hours", type=float, default=6.0)
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit (Task Scheduler mode)")
    parser.add_argument("--retrain", action="store_true", help="Retrain the ranker when enough new events exist")
    args = parser.parse_args()

    if args.once:
        run_cycle(retrain=args.retrain)
        return
    while True:
        run_cycle(retrain=args.retrain)
        time.sleep(max(60, int(args.interval_hours * 3600)))


if __name__ == "__main__":
    main()
