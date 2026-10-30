from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from ..config import settings
from .errors import IntegrationNotConfigured, IntegrationResponseError


def _value(record: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if record.get(key) not in (None, ""):
            return record[key]
    return default


def normalize_scheme(record: dict[str, Any]) -> dict[str, Any]:
    eligibility = _value(record, "eligibility", "eligibility_json", default={})
    if isinstance(eligibility, str):
        eligibility = {"raw": eligibility}
    return {
        "id": str(_value(record, "id", "scheme_id", "schemeId", "_id", default="scheme-external")),
        "name": _value(record, "scheme_name", "schemeName", "name", "title", default="Government scheme"),
        "ministry": _value(record, "ministry", "department", "nodal_ministry", default="Government of India"),
        "category": _value(record, "category", "scheme_category", default="Career"),
        "benefit": _value(record, "benefit", "benefits", "description", default="See official scheme details"),
        "eligibility": eligibility,
        "application_url": _value(record, "application_url", "url", "official_url"),
        "state": _value(record, "state", "state_name", default="India"),
        "posted_at": _value(record, "posted_at", "updated_at", default=datetime.now(timezone.utc).isoformat()),
        "type": "scheme",
    }


def fetch_myscheme(limit: int = 1000) -> list[dict[str, Any]]:
    if not settings.myscheme_api_url or not settings.myscheme_api_key:
        raise IntegrationNotConfigured("Set MYSCHEME_API_URL and MYSCHEME_API_KEY to ingest official schemes.")
    params: dict[str, Any] = {"api-key": settings.myscheme_api_key, "format": "json", "limit": limit}
    if settings.myscheme_resource_id:
        params["resource_id"] = settings.myscheme_resource_id
    response = httpx.get(settings.myscheme_api_url, params=params, timeout=60)
    if response.status_code >= 400:
        raise IntegrationResponseError(f"MyScheme/data.gov.in request failed with HTTP {response.status_code}.")
    payload = response.json()
    records = payload.get("records", payload.get("data", payload)) if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise IntegrationResponseError("MyScheme response did not contain records/data.")
    return [normalize_scheme(record) for record in records if isinstance(record, dict)]
