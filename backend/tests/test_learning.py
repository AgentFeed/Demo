from __future__ import annotations

import json
from pathlib import Path

from app.learning import LogisticRanker, evaluate_ranker, load_training_examples, temporal_split


ROOT = Path(__file__).resolve().parents[1]


def test_demo_dataset_trains_and_evaluates_temporally(tmp_path) -> None:
    dataset = ROOT / "training" / "demo_interactions.csv"
    users = ROOT / "training" / "demo_users.csv"
    items = ROOT / "training" / "demo_jobs.csv"
    examples = load_training_examples(dataset, users_path=users, items_path=items)
    train, validation = temporal_split(examples)
    model = LogisticRanker.empty().fit(train, epochs=80)
    metrics = evaluate_ranker(model, validation)

    assert len(examples) == 41
    assert train and validation
    assert set(model.feature_names) >= {"relevance", "skill_overlap", "is_job"}
    assert 0 <= metrics["ndcg_at_10"] <= 1
    assert metrics["users"] == 4

    output = tmp_path / "ranker.json"
    model.save(output)
    restored = LogisticRanker.load(output)
    assert restored is not None
    assert restored.predict({name: 0.5 for name in restored.feature_names}) == model.predict({name: 0.5 for name in model.feature_names})


def test_loader_accepts_jth_style_aliases(tmp_path) -> None:
    interactions = tmp_path / "events.json"
    interactions.write_text(json.dumps({"events": [
        {"candidate_id": "c1", "vacancy_id": "v1", "event_type": "application", "created_at": "2026-01-01T00:00:00Z"},
        {"candidate_id": "c1", "vacancy_id": "v2", "event_type": "impression", "created_at": "2026-01-02T00:00:00Z"},
    ]}), encoding="utf-8")
    users = tmp_path / "users.json"
    users.write_text(json.dumps([{"candidate_id": "c1", "skills": ["Python"], "city": "Pune"}]), encoding="utf-8")
    items = tmp_path / "jobs.json"
    items.write_text(json.dumps([{"vacancy_id": "v1", "title": "Python role", "skills": ["Python"], "location": "Pune"}, {"vacancy_id": "v2", "title": "Sales role", "skills": ["Sales"], "location": "Delhi"}]), encoding="utf-8")

    examples = load_training_examples(interactions, users_path=users, items_path=items)

    assert [example.action for example in examples] == ["apply", "impression"]
    assert examples[0].user["skills"] == ["Python"]
    assert examples[0].item["title"] == "Python role"
