from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {"X-Demo-User": "demo_fresher"}


def test_health_and_me_contract() -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    me = client.get("/api/users/me", headers=HEADERS)
    assert me.status_code == 200
    assert me.json()["user"]["id"] == "demo_fresher"


def test_feed_runs_all_six_agents_and_returns_explanation() -> None:
    response = client.get("/api/feed?limit=10", headers=HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["items"]
    assert [step["agent"] for step in body["agent_trace"]] == [
        "profiler", "interest_miner", "matcher", "social_connector", "coach_gap", "feed_ranker"
    ]
    assert all("breakdown" in item for item in body["items"])
    assert all("why" in item for item in body["items"])
    assert body["backends"]["orchestrator_backend"] in {"langgraph", "sequential-fallback"}


def test_interaction_changes_persistent_feed_memory() -> None:
    interaction = client.post(
        "/api/interactions",
        headers=HEADERS,
        json={"item_id": "j1", "item_type": "job", "action": "hide", "reason": "Rotating shifts"},
    )
    assert interaction.status_code == 200
    me = client.get("/api/users/me", headers=HEADERS)
    assert me.status_code == 200
    assert "Rotating shifts" in me.json()["user"]["hates"]
    feed = client.get("/api/feed?limit=50&type=job", headers=HEADERS)
    assert feed.status_code == 200
    assert all(item["id"] != "j1" for item in feed.json()["items"])


def test_resume_parse_referral_and_source_contracts() -> None:
    resume = client.post(
        "/api/resume/parse",
        headers=HEADERS,
        files={"file": ("resume.pdf", b"Sudipta React TypeScript Python SQL project", "application/pdf")},
    )
    assert resume.status_code == 200
    assert resume.json()["ats_score"] >= 68
    assert "React" in resume.json()["resume_json"]["skills"]

    referral = client.get("/api/peers/referral-path?job_id=j1", headers=HEADERS)
    assert referral.status_code == 200
    assert len(referral.json()["path"]) == 3
    assert referral.json()["draft_hinglish"]

    sources = client.get("/api/jobs/sources", headers=HEADERS)
    assert sources.status_code == 200
    assert sources.json()["freehire"] > 0
    assert sources.json()["kaggle_india"] > 0



def test_model_status_and_impression_contract() -> None:
    model = client.get("/api/model/status", headers=HEADERS)
    assert model.status_code == 200
    assert model.json()["available"] is True
    assert model.json()["backend"] == "learned-logistic+guardrails"

    response = client.post(
        "/api/impressions",
        headers=HEADERS,
        json={"impressions": [{"item_id": "j1", "item_type": "job", "rank_position": 1, "model_version": model.json()["model_version"], "context": {"tab": "all"}}]},
    )
    assert response.status_code == 200
    assert response.json()["recorded"] == 1
