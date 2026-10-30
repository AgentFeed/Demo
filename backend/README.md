# Bharat Career Twin backend

This is the backend for the AgentFeed demo and production-shaped integration
path. It follows the project plan's six-agent flow:

`Profiler → Interest Miner → Matcher → Social Connector → Coach Gap → Feed Ranker`

SQLite/local lexical matching remains the default so the project runs without
credentials. Real integrations are enabled with `BCT_STORE_BACKEND=supabase`
and the environment variables in `.env.example`. The production-shaped
Postgres/pgvector schema and RPC retrieval functions are in
`../supabase/migrations/01_schema.sql`.

## Run

From `BHARAT_CAREER_TWIN_PLAN/backend`:

```bash
python3 -m pip install -r requirements.txt
# For LangGraph, Groq, Supabase, freehire Postgres, and embeddings:
python3 -m pip install -r requirements-integrations.txt
uvicorn app.main:app --reload --port 8000
```

Apply the Supabase migration before starting production mode. The migration
creates the pgvector indexes, RLS policies, startup applications table, and
the `match_jobs`, `match_schemes`, `match_startups`, and `match_users` RPCs
used by the Matcher agent.

The API health response exposes the active provider state. A real configured
deployment should report `store: supabase`, `supabase: true`, `groq: true`,
`langgraph: true`, and `embeddings: true`; the local demo reports its
deterministic fallbacks instead. The local demo also reports the generated
learned ranker through `ranker: true`. `/api/feed` also returns a `backends` object
so the ranking response is inspectable.

Useful local identities:

- `demo_fresher`
- `demo_govt`
- `demo_founder`

Pass one through `X-Demo-User` or `?user_id=demo_fresher`. The default is
`demo_fresher`. Production should replace this dependency with Supabase JWT
verification.

## Contract highlights

- `GET /health`
- `GET /api/feed?limit=20&type=all&steer=more%20local%20roles`
- `POST /api/interactions`
- `POST /api/impressions`
- `GET /api/model/status`
- `POST /api/resume/parse`
- `GET /api/peers/referral-path?job_id=j1`
- `GET /api/jobs/sources`
- `POST /api/sync/freehire`
- `POST /api/ingest/jobs` with `{ "csv_url": "..." }`
- `POST /api/ingest/schemes`
- `GET /docs`

`app/cron/sync_freehire.py` accepts a freehire JSON export and upserts by
`freehire_id`, preserving the duplicate-safe sync behavior required by the
project plan. Run it from the backend directory with:

```bash
python3 -m app.cron.sync_freehire /path/to/freehire-export.json
```

Without a path, the CLI can use `FREEHIRE_DATABASE_URL`, `FREEHIRE_JSON_URL`,
or the public/API-key-backed Freehire API configured in the environment.

## Train the learned ranker

The repository includes a small, reproducible training fixture so the project
can demonstrate a real train/evaluate/save/load loop without external keys:

```bash
python3 -m app.cron.train_ranker
```

This writes `backend/models/ranker.json`. To turn local product usage into a retraining dataset first, export impressions plus actions:

```bash
python3 -m app.cron.export_training --output-dir training/exported
python3 -m app.cron.train_ranker \
  --dataset training/exported/interactions.csv \
  --users training/exported/users.csv \
  --items training/exported/items.csv
```

For JTH, XING, or CareerBuilder-shaped
exports, pass an interactions file plus optional user and item catalogs:

```bash
python3 -m app.cron.train_ranker \
  --dataset /path/to/interactions.csv \
  --users /path/to/users.csv \
  --items /path/to/jobs.csv \
  --output models/ranker.json
```

Supported interaction aliases include `user_id`/`candidate_id`,
`job_id`/`vacancy_id`, `action`/`event_type`, and `timestamp`/`created_at`.
The learned artifact is dependency-free JSON and is loaded automatically by the
Feed Ranker for job items. Set `BCT_RANKER_MODEL_PATH` to select another artifact.

The UI/API logs exposure rows through `POST /api/impressions`; training should
prefer impressions plus observed actions over treating every unseen item as a
negative. `GET /api/model/status` exposes the active model version and metrics.
