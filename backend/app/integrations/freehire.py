from __future__ import annotations

import csv
import io
import json
from typing import Any, Iterable

import httpx

from ..config import settings
from .errors import IntegrationNotConfigured, IntegrationResponseError


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("data", "jobs", "postings", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    raise IntegrationResponseError("Freehire response did not contain a jobs/postings array.")


def normalize_posting(posting: dict[str, Any]) -> dict[str, Any]:
    return {
        "freehire_id": posting.get("freehire_id") or posting.get("public_slug") or posting.get("id") or posting.get("posting_id") or posting.get("external_id"),
        "title": posting.get("title") or posting.get("job_title") or "Untitled role",
        "company": posting.get("company") or posting.get("company_name") or "Unknown company",
        "location": posting.get("location") or posting.get("location_city") or posting.get("locations") or "Remote",
        "location_state": posting.get("location_state") or posting.get("state") or "",
        "description": posting.get("description") or posting.get("job_description") or "",
        "url": posting.get("url") or posting.get("source_url") or posting.get("job_url"),
        "board": posting.get("board") or posting.get("source") or "freehire",
        "provider": posting.get("provider") or "freehire",
        "posted_at": posting.get("posted_at") or posting.get("published_at") or posting.get("created_at"),
        "skills": posting.get("skills") or [],
        "salary": posting.get("salary") or posting.get("salary_text") or "Not listed",
    }


def fetch_freehire_api(*, max_pages: int | None = None, page_size: int = 100) -> list[dict[str, Any]]:
    if not settings.freehire_api_url:
        raise IntegrationNotConfigured("Set FREEHIRE_API_URL, FREEHIRE_JSON_URL, or FREEHIRE_DATABASE_URL.")
    results: list[dict[str, Any]] = []
    max_pages = max_pages or settings.freehire_max_pages
    for page in range(max_pages):
        headers = {"Authorization": f"Bearer {settings.freehire_api_key}"} if settings.freehire_api_key else {}
        response = httpx.get(settings.freehire_api_url, headers=headers, params={"limit": page_size, "offset": page * page_size}, timeout=60)
        if response.status_code >= 400:
            raise IntegrationResponseError(f"Freehire API failed with HTTP {response.status_code}.")
        batch = _records(response.json())
        if not batch:
            break
        results.extend(normalize_posting(item) for item in batch)
        if len(batch) < page_size:
            break
    return results


def fetch_freehire_json(url: str | None = None) -> list[dict[str, Any]]:
    target = url or settings.freehire_json_url
    if not target:
        raise IntegrationNotConfigured("Set FREEHIRE_JSON_URL to use JSON freehire ingestion.")
    if target.startswith(("http://", "https://")):
        response = httpx.get(target, timeout=60)
        if response.status_code >= 400:
            raise IntegrationResponseError(f"Freehire JSON endpoint failed with HTTP {response.status_code}.")
        payload = response.json()
    else:
        with open(target, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    return [normalize_posting(item) for item in _records(payload)]


def fetch_freehire_database(database_url: str | None = None, *, limit: int = 5000) -> list[dict[str, Any]]:
    target = database_url or settings.freehire_database_url
    if not target:
        raise IntegrationNotConfigured("Set FREEHIRE_DATABASE_URL to use freehire Postgres ingestion.")
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - depends on real install
        raise IntegrationNotConfigured("Install psycopg[binary] for freehire Postgres ingestion.") from exc
    query = """
        select id, company, title, description, location, url, published_at, board
        from postings
        order by published_at desc nulls last
        limit %s
    """
    with psycopg.connect(target) as connection, connection.cursor() as cursor:
        cursor.execute(query, (limit,))
        columns = [column.name for column in cursor.description]
        return [normalize_posting(dict(zip(columns, row))) for row in cursor.fetchall()]


def load_configured_freehire() -> list[dict[str, Any]]:
    if settings.freehire_database_url:
        return fetch_freehire_database()
    if settings.freehire_json_url:
        return fetch_freehire_json()
    return fetch_freehire_api()


def load_csv_jobs(content: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(content))
    jobs: list[dict[str, Any]] = []
    for index, row in enumerate(reader):
        clean = {str(key).strip().lower().replace(" ", "_"): value for key, value in row.items() if key}
        skills = clean.get("skills") or clean.get("required_skills") or ""
        if isinstance(skills, str):
            skills = [value.strip() for value in skills.replace("|", ",").split(",") if value.strip()]
        jobs.append(normalize_posting({
            "freehire_id": clean.get("id") or clean.get("job_id") or f"kaggle-{index + 1}",
            "title": clean.get("title") or clean.get("job_title") or clean.get("job_title_name"),
            "company": clean.get("company") or clean.get("company_name"),
            "location": clean.get("location") or clean.get("city"),
            "description": clean.get("description") or clean.get("job_description"),
            "salary": clean.get("salary") or clean.get("salary_estimate") or clean.get("salary_range"),
            "posted_at": clean.get("posted_at") or clean.get("date_posted"),
            "skills": skills,
            "url": clean.get("url") or clean.get("job_url"),
            "board": "kaggle_india",
            "provider": "kaggle_india",
        }))
    return jobs


def fetch_csv_jobs(url: str) -> list[dict[str, Any]]:
    if url.startswith(("http://", "https://")):
        response = httpx.get(url, timeout=60)
        if response.status_code >= 400:
            raise IntegrationResponseError(f"CSV job source failed with HTTP {response.status_code}.")
        return load_csv_jobs(response.text)
    with open(url, "r", encoding="utf-8", newline="") as handle:
        return load_csv_jobs(handle.read())
