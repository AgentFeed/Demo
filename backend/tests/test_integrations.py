from __future__ import annotations

from types import SimpleNamespace

from app.integrations.freehire import fetch_freehire_api, normalize_posting
from app.integrations.groq_client import GroqJsonClient
from app.integrations.myscheme import normalize_scheme
from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)
HEADERS = {"X-Demo-User": "demo_fresher"}


def test_freehire_normalizes_v1_envelope_shape(monkeypatch) -> None:
    response = SimpleNamespace(status_code=200, json=lambda: {"data": [{"public_slug": "react-acme-123", "title": "React Engineer", "company": "Acme", "location": "Remote", "url": "https://example.test/job", "posted_at": "2026-10-22T10:00:00Z", "skills": ["react"]}]})
    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: response)

    jobs = fetch_freehire_api(max_pages=1, page_size=100)

    assert jobs[0]["freehire_id"] == "react-acme-123"
    assert jobs[0]["company"] == "Acme"
    assert normalize_posting({"external_id": "ext-1"})["freehire_id"] == "ext-1"


def test_myscheme_normalizes_official_record_fields() -> None:
    scheme = normalize_scheme({"schemeId": "m-1", "schemeName": "Skill India", "ministry": "MSDE", "benefits": "Training", "eligibility": {"state": True}})

    assert scheme["id"] == "scheme-external" or scheme["id"] == "m-1"
    assert scheme["name"] == "Skill India"
    assert scheme["eligibility"]["state"] is True


def test_groq_json_client_parses_structured_completion() -> None:
    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["response_format"] == {"type": "json_object"}
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"skills":["React"]}'))])

    fake = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))
    client = GroqJsonClient(api_key="test-key")
    client._client = fake

    assert client.json_completion("system", "user")["skills"] == ["React"]


def test_ingestion_routes_wire_adapters_into_local_store(monkeypatch) -> None:
    monkeypatch.setattr("app.main.fetch_csv_jobs", lambda _url: [{"freehire_id": "integration-csv-1", "title": "CSV role", "company": "CSV Co", "location": "Nagpur", "skills": ["React"]}])
    monkeypatch.setattr("app.main.fetch_myscheme", lambda: [{"id": "integration-scheme-1", "name": "Integration scheme", "ministry": "Test ministry", "eligibility": {"state": True}}])
    monkeypatch.setattr("app.main.load_configured_freehire", lambda: [{"freehire_id": "integration-freehire-1", "title": "Live role", "company": "Freehire Co", "location": "Remote", "skills": ["Python"]}])

    jobs = client.post("/api/ingest/jobs", headers=HEADERS, json={"csv_url": "mock://jobs.csv"})
    schemes = client.post("/api/ingest/schemes", headers=HEADERS)
    freehire = client.post("/api/sync/freehire", headers=HEADERS)

    assert jobs.status_code == 200 and jobs.json()["inserted"] + jobs.json()["updated"] == 1
    assert schemes.status_code == 200 and schemes.json()["inserted"] + schemes.json()["updated"] == 1
    assert freehire.status_code == 200 and freehire.json()["inserted"] + freehire.json()["updated"] == 1
