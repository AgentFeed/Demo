"""Dependency-free learning and evaluation utilities for the career ranker."""

from __future__ import annotations

import csv
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

FEATURE_NAMES = (
    "relevance", "skill_overlap", "location_match", "social", "freshness",
    "popularity", "eligibility", "hate", "referral", "feedback", "is_job",
)

ACTION_TARGETS = {
    "impression": 0.0, "view": 0.18, "click": 0.35, "like": 0.55,
    "share": 0.65, "save": 0.72, "apply": 0.92, "referral": 1.0,
    "hide": 0.0, "delete": 0.0,
}
POSITIVE_ACTIONS = {"view", "click", "like", "share", "save", "apply", "referral"}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, (tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass
    return [part.strip() for part in text.replace("|", ",").split(",") if part.strip()]


def _normalise(value: Any) -> str:
    return " ".join(str(value or "").lower().replace("/", " ").replace("-", " ").split())


def _tokens(values: Iterable[Any]) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        text = _normalise(value)
        if text:
            tokens.update(text.split())
            tokens.add(text)
    return tokens


def _first(record: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return default


def _parse_datetime(value: Any, fallback_index: int = 0) -> datetime:
    if value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime(2020, 1, 1, tzinfo=timezone.utc) + timedelta(days=fallback_index)


def _freshness(value: Any, timestamp: datetime | None = None) -> float:
    hours = _as_float(value, -1)
    if hours < 0 and timestamp:
        hours = max(0.0, (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600)
    return math.exp(-max(0.0, hours if hours >= 0 else 12) / 72)


def _action_name(value: Any, label: Any = None) -> str:
    text = _normalise(value).replace(" ", "_")
    aliases = {
        "impression": "impression", "impressions": "impression", "shown": "impression",
        "display": "impression", "displayed": "impression", "view": "view", "viewed": "view",
        "click": "click", "clicked": "click", "bookmark": "save", "bookmarked": "save",
        "save": "save", "saved": "save", "apply": "apply", "applied": "apply",
        "application": "apply", "reply": "apply", "reply_click": "apply", "like": "like",
        "liked": "like", "share": "share", "shared": "share", "referral": "referral",
        "hide": "hide", "hidden": "hide", "delete": "delete", "deleted": "delete",
    }
    if text in aliases:
        return aliases[text]
    if label is not None:
        return "click" if _as_float(label) > 0 else "impression"
    return "impression"


def _catalog_key(record: dict[str, Any], kind: str) -> str:
    if kind == "user":
        keys = ("user_id", "userId", "candidate_id", "candidateId", "member_id", "memberId", "id")
    else:
        keys = ("item_id", "itemId", "job_id", "jobId", "vacancy_id", "vacancyId", "posting_id", "id")
    return str(_first(record, *keys, default="")).strip()


def _merge_catalog(record: dict[str, Any], catalog: dict[str, dict[str, Any]], kind: str) -> dict[str, Any]:
    merged = dict(catalog.get(_catalog_key(record, kind), {}))
    merged.update(record)
    return merged


@dataclass(frozen=True)
class TrainingExample:
    user_id: str
    item_id: str
    action: str
    target: float
    timestamp: str
    user: dict[str, Any]
    item: dict[str, Any]


def _normalise_example(record: dict[str, Any], users: dict[str, dict[str, Any]], items: dict[str, dict[str, Any]], index: int) -> TrainingExample | None:
    user_id = _catalog_key(record, "user")
    item_id = _catalog_key(record, "item")
    if not user_id or not item_id:
        return None
    action = _action_name(
        _first(record, "action", "event", "event_type", "eventType", "interaction", "interaction_type", "stage"),
        _first(record, "label", "relevance", "target", default=None),
    )
    parsed_time = _parse_datetime(_first(record, "timestamp", "created_at", "createdAt", "event_time", "date", default=None), index)
    target = _as_float(_first(record, "target", "label", "relevance", default=ACTION_TARGETS.get(action, 0.0)), ACTION_TARGETS.get(action, 0.0))
    return TrainingExample(
        user_id=user_id,
        item_id=item_id,
        action=action,
        target=max(0.0, min(1.0, target)),
        timestamp=parsed_time.isoformat(),
        user=_merge_catalog(record, users, "user"),
        item=_merge_catalog(record, items, "item"),
    )


def _read_records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    if source.suffix.lower() in {".json", ".jsonl"}:
        text = source.read_text(encoding="utf-8")
        if source.suffix.lower() == ".jsonl":
            return [json.loads(line) for line in text.splitlines() if line.strip()]
        data = json.loads(text)
        if isinstance(data, dict):
            for key in ("interactions", "events", "records", "data"):
                if isinstance(data.get(key), list):
                    return [row for row in data[key] if isinstance(row, dict)]
            return [data]
        return [row for row in data if isinstance(row, dict)]
    with source.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_training_examples(path: str | Path, users_path: str | Path | None = None, items_path: str | Path | None = None) -> list[TrainingExample]:
    users: dict[str, dict[str, Any]] = {}
    items: dict[str, dict[str, Any]] = {}
    if users_path:
        for record in _read_records(users_path):
            if _catalog_key(record, "user"):
                users[_catalog_key(record, "user")] = record
    if items_path:
        for record in _read_records(items_path):
            if _catalog_key(record, "item"):
                items[_catalog_key(record, "item")] = record
    examples = [_normalise_example(row, users, items, index) for index, row in enumerate(_read_records(path))]
    return [example for example in examples if example is not None]


def _user_skills(user: dict[str, Any]) -> list[str]:
    return _as_list(_first(user, "skills", "user_skills", "skill_tags", default=[]))


def _user_interests(user: dict[str, Any]) -> list[str]:
    return _as_list(_first(user, "interests", "user_interests", "interest_tags", default=[]))


def _item_skills(item: dict[str, Any]) -> list[str]:
    return _as_list(_first(item, "skills", "item_skills", "required_skills", "skill_tags", default=[]))


def build_feature_vector(
    user: dict[str, Any],
    item: dict[str, Any],
    *,
    interest_tags: Iterable[str] | None = None,
    hate_tags: Iterable[str] | None = None,
    interaction_signal: float = 0.0,
    timestamp: datetime | None = None,
) -> dict[str, float]:
    user_skills = _user_skills(user)
    interests = [*_user_interests(user), *(interest_tags or [])]
    hates = [*_as_list(_first(user, "hates", "hate_tags", default=[])), *(hate_tags or [])]
    item_skills = _item_skills(item)
    user_terms = _tokens([*user_skills, *interests])
    item_terms = _tokens([*item_skills, _first(item, "title", "name", "role", default=""), _first(item, "description", "summary", default="")])
    skill_terms = _tokens(item_skills)
    skill_overlap = len(user_terms & skill_terms) / max(1, len(skill_terms)) if skill_terms else 0.0
    text_overlap = len(user_terms & item_terms) / max(1, len(user_terms)) if user_terms else 0.0
    relevance = max(0.0, min(1.0, 0.55 * skill_overlap + 0.45 * text_overlap))
    user_location = _normalise(_first(user, "city", "location", "location_city", default=""))
    item_location = _normalise(_first(item, "location", "location_city", "city", default=""))
    location_match = 1.0 if user_location and item_location and (user_location in item_location or item_location in user_location or "remote" in item_location) else 0.0
    social = _as_float(_first(item, "social_score", "social", "mutual_score", default=0.0))
    social = min(1.0, social / 5) if social > 1 else max(0.0, social)
    likes = _as_float(_first(item, "likes", "likes_count", default=0.0))
    saves = _as_float(_first(item, "saves", "saves_count", default=0.0))
    popularity = min(1.0, math.log1p(max(0.0, likes + saves * 2)) / math.log(120)) if likes or saves else 0.0
    raw_eligibility = _first(item, "eligibility_score", "eligibility", default=0.0)
    if isinstance(raw_eligibility, dict):
        eligibility = sum(1 for value in raw_eligibility.values() if bool(value)) / max(1, len(raw_eligibility))
    else:
        eligibility = _as_float(raw_eligibility)
        if eligibility > 1:
            eligibility /= 100
    item_text = _normalise(" ".join([str(_first(item, "title", "name", default="")), *_item_skills(item), str(_first(item, "description", default=""))]))
    hate = 1.0 if any(_normalise(tag) and _normalise(tag) in item_text for tag in hates) else 0.0
    freshness = _freshness(_first(item, "fresh_hours", "age_hours", default=-1), timestamp)
    referral = 1.0 if bool(_first(item, "has_referral", "referral_path_exists", "referral", default=False)) else 0.0
    return {
        "relevance": relevance,
        "skill_overlap": max(0.0, min(1.0, skill_overlap)),
        "location_match": location_match,
        "social": max(0.0, min(1.0, social)),
        "freshness": max(0.0, min(1.0, freshness)),
        "popularity": max(0.0, min(1.0, popularity)),
        "eligibility": max(0.0, min(1.0, eligibility)),
        "hate": hate,
        "referral": referral,
        "feedback": max(-1.0, min(1.0, _as_float(interaction_signal))),
        "is_job": 1.0 if _normalise(_first(item, "type", "item_type", default="job")) == "job" else 0.0,
    }


def example_features(example: TrainingExample) -> dict[str, float]:
    return build_feature_vector(example.user, example.item, timestamp=_parse_datetime(example.timestamp))


@dataclass
class LogisticRanker:
    feature_names: tuple[str, ...]
    weights: list[float]
    bias: float = 0.0
    model_version: str = "logistic-v1"
    trained_examples: int = 0
    metrics: dict[str, float] | None = None

    @classmethod
    def empty(cls) -> "LogisticRanker":
        return cls(FEATURE_NAMES, [0.0 for _ in FEATURE_NAMES])

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, value))))

    def predict(self, features: dict[str, float]) -> float:
        value = self.bias + sum(weight * _as_float(features.get(name)) for name, weight in zip(self.feature_names, self.weights))
        return self._sigmoid(value)

    def fit(self, examples: list[TrainingExample], epochs: int = 300, learning_rate: float = 0.08, l2: float = 0.002) -> "LogisticRanker":
        if not examples:
            raise ValueError("At least one training example is required.")
        vectors = [example_features(example) for example in examples]
        self.weights = [0.0 for _ in self.feature_names]
        self.bias = 0.0
        for _ in range(max(1, epochs)):
            gradients = [0.0 for _ in self.feature_names]
            bias_gradient = 0.0
            for example, vector in zip(examples, vectors):
                error = self.predict(vector) - example.target
                for index, name in enumerate(self.feature_names):
                    gradients[index] += error * vector[name]
                bias_gradient += error
            scale = 1.0 / max(1, len(examples))
            for index in range(len(self.weights)):
                gradients[index] = gradients[index] * scale + l2 * self.weights[index]
                self.weights[index] -= learning_rate * gradients[index]
            self.bias -= learning_rate * bias_gradient * scale
        self.trained_examples = len(examples)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_type": "logistic_ranker",
            "model_version": self.model_version,
            "feature_names": list(self.feature_names),
            "weights": self.weights,
            "bias": self.bias,
            "trained_examples": self.trained_examples,
            "metrics": self.metrics or {},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LogisticRanker":
        names = tuple(str(item) for item in data.get("feature_names") or FEATURE_NAMES)
        weights = [float(item) for item in data.get("weights") or [0.0 for _ in names]]
        return cls(names, weights, float(data.get("bias", 0.0)), str(data.get("model_version", "logistic-v1")), int(data.get("trained_examples", 0)), dict(data.get("metrics") or {}))

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return destination

    @classmethod
    def load(cls, path: str | Path) -> "LogisticRanker | None":
        source = Path(path)
        if not source.exists():
            return None
        try:
            return cls.from_dict(json.loads(source.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None


def default_model_path() -> Path:
    configured = os.getenv("BCT_RANKER_MODEL_PATH")
    return Path(configured) if configured else Path(__file__).resolve().parents[1] / "models" / "ranker.json"


def load_runtime_ranker() -> LogisticRanker | None:
    return LogisticRanker.load(default_model_path())


def _binary_target(example: TrainingExample) -> int:
    return 1 if example.action in POSITIVE_ACTIONS or example.target >= 0.5 else 0


def _dcg(values: list[int]) -> float:
    return sum(value / math.log2(index + 2) for index, value in enumerate(values))


def evaluate_ranker(rank_model: LogisticRanker, examples: list[TrainingExample], k: int = 10) -> dict[str, float]:
    groups: dict[str, list[TrainingExample]] = {}
    for example in examples:
        groups.setdefault(example.user_id, []).append(example)
    ndcg_values: list[float] = []
    recall_values: list[float] = []
    reciprocal_values: list[float] = []
    for rows in groups.values():
        ranked = sorted(rows, key=lambda row: rank_model.predict(example_features(row)), reverse=True)[:k]
        relevance = [_binary_target(row) for row in ranked]
        positives = sum(_binary_target(row) for row in rows)
        ideal = sorted((_binary_target(row) for row in rows), reverse=True)[:k]
        ideal_dcg = _dcg(ideal)
        ndcg_values.append(_dcg(relevance) / ideal_dcg if ideal_dcg else 0.0)
        recall_values.append(sum(relevance) / positives if positives else 0.0)
        reciprocal_values.append(next((1.0 / (index + 1) for index, value in enumerate(relevance) if value), 0.0))
    return {
        f"ndcg_at_{k}": sum(ndcg_values) / max(1, len(ndcg_values)),
        f"recall_at_{k}": sum(recall_values) / max(1, len(recall_values)),
        "mrr": sum(reciprocal_values) / max(1, len(reciprocal_values)),
        "users": float(len(groups)),
        "examples": float(len(examples)),
    }


def temporal_split(examples: list[TrainingExample], validation_ratio: float = 0.2) -> tuple[list[TrainingExample], list[TrainingExample]]:
    ordered = sorted(examples, key=lambda row: row.timestamp)
    if len(ordered) < 2:
        return ordered, []
    split_index = max(1, min(len(ordered) - 1, int(len(ordered) * (1 - validation_ratio))))
    return ordered[:split_index], ordered[split_index:]


def train_from_dataset(path: str | Path, output: str | Path, users_path: str | Path | None = None, items_path: str | Path | None = None, epochs: int = 300) -> dict[str, Any]:
    examples = load_training_examples(path, users_path=users_path, items_path=items_path)
    train_examples, validation_examples = temporal_split(examples)
    if not train_examples:
        raise ValueError("The dataset did not contain usable interaction rows.")
    model = LogisticRanker.empty().fit(train_examples, epochs=epochs)
    metrics = evaluate_ranker(model, validation_examples or train_examples)
    model.metrics = metrics
    model.save(output)
    return {
        "model_path": str(output), "model_version": model.model_version,
        "trained_examples": len(train_examples), "validation_examples": len(validation_examples),
        "metrics": metrics,
    }
