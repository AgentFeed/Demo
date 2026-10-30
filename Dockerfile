FROM python:3.11-slim

# Hugging Face Spaces runs the container as UID 1000
RUN useradd -m -u 1000 user
WORKDIR /code

COPY backend/requirements.txt /code/backend/requirements.txt
RUN pip install --no-cache-dir -r /code/backend/requirements.txt

COPY backend /code/backend
COPY data/demo_catalog.jsonl /code/data/demo_catalog.jsonl

# Build the demo database at image-build time:
# seeded demo users/schemes/peers + 4.5k real Naukri jobs + best-effort live sync
RUN cd /code/backend \
 && BCT_DB_PATH=/code/data/bharat_twin.db python -c "from app.runtime import create_store; create_store()" \
 && BCT_DB_PATH=/code/data/bharat_twin.db python -m app.cron.ingest_naukri_hf --file /code/data/demo_catalog.jsonl
RUN cd /code/backend \
 && BCT_DB_PATH=/code/data/bharat_twin.db timeout 180 python -m app.cron.sync_freehire \
 || echo "freehire sync skipped at build; live jobs will be absent until first sync"

RUN chown -R user:user /code
USER user
ENV BCT_DB_PATH=/code/data/bharat_twin.db

WORKDIR /code/backend
EXPOSE 7860
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
