# Training data contract

This folder contains the data used by the learned job ranker.

## Files

- `demo_users.csv`, `demo_jobs.csv`, `demo_interactions.csv`: tiny reproducible
  fixture (4 users, 7 jobs). Pipeline smoke test only.
- `simulated/`: ~19.6k interactions from 400 simulated users acting on the
  REAL ingested Naukri catalog (`app/cron/simulate_interactions.py`).
  Behaviour is simulated, the jobs are real. Regenerate:
  `python -m app.cron.simulate_interactions`.
- `evaluation_report.md`: popularity vs hybrid-rules vs learned-logistic on the
  same temporal split (`app/cron/evaluate_baselines.py`).
- `careerbuilder/`: created by `app/cron/convert_careerbuilder.py` once the
  Kaggle CareerBuilder export is downloaded (real application labels).

## Real data sources (record in the report: source, date, license)

| Role | Source | Status |
|---|---|---|
| India job catalog (32k) | `muhammetakkurt/naukri-jobs-dataset` (HuggingFace, CC-BY-NC-4.0) | ingested via `app/cron/ingest_naukri_hf.py` |
| Live recent jobs | freehire.me public API, India/remote filtered | `app/cron/sync_freehire.py` |
| Real interaction labels | Kaggle CareerBuilder Job Recommendation Challenge | converter ready, download required |

## Interaction columns

Required: `user_id`, `item_id`, `action`, `timestamp`.

Accepted aliases include:

- user: `user_id`, `userId`, `candidate_id`, `member_id`
- item: `item_id`, `itemId`, `job_id`, `vacancy_id`, `posting_id`
- event: `action`, `event`, `event_type`, `interaction_type`, `stage`
- time: `timestamp`, `created_at`, `event_time`, `date`
- label: `label`, `relevance`, `target`

The loader accepts CSV, JSON arrays/objects, and JSONL. `impression` is a
logged exposure with a zero target; `hide`/`delete` are negative boundaries;
click, save, apply, referral, and similar actions receive progressively higher
training targets. Unseen jobs are not automatically converted into negatives.

## Train

```bash
cd backend
# train on the simulated-on-real-catalog dataset (current default model)
python -m app.cron.train_ranker --epochs 1500 \
  --dataset training/simulated/interactions.csv \
  --users training/simulated/users.csv \
  --items training/simulated/items.csv

# train on real CareerBuilder labels (after downloading + converting)
python -m app.cron.convert_careerbuilder --data-dir ../data/raw/careerbuilder
python -m app.cron.train_ranker --epochs 1500 \
  --dataset training/careerbuilder/interactions.csv \
  --users training/careerbuilder/users.csv \
  --items training/careerbuilder/items.csv

# compare popularity vs rules vs learned
python -m app.cron.evaluate_baselines --epochs 1500 \
  --dataset training/simulated/interactions.csv \
  --users training/simulated/users.csv \
  --items training/simulated/items.csv \
  --report training/evaluation_report.md
```

The artifact is dependency-free JSON and contains the feature names, weights,
model version, training count, and temporal validation metrics.
