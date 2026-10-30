from __future__ import annotations

import math
from typing import Any

from ..learning import build_feature_vector, load_runtime_ranker
from .state import AgentState


RULE_WEIGHTS = {
    "relevance": .35,
    "skill_overlap": .20,
    "social": .15,
    "freshness": .12,
    "popularity": .08,
    "eligibility": .10,
    "hate": .40,
}


def _similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
    a = {str(value).lower() for value in left.get("skills") or []}
    b = {str(value).lower() for value in right.get("skills") or []}
    union = a | b
    return len(a & b) / len(union) if union else 0


def _rule_score(features: dict[str, float], item: dict[str, Any]) -> float:
    score = (
        RULE_WEIGHTS["relevance"] * features["relevance"]
        + RULE_WEIGHTS["skill_overlap"] * features["skill_overlap"]
        + RULE_WEIGHTS["social"] * features["social"]
        + RULE_WEIGHTS["freshness"] * features["freshness"]
        + RULE_WEIGHTS["popularity"] * features["popularity"]
        + RULE_WEIGHTS["eligibility"] * features["eligibility"]
        - RULE_WEIGHTS["hate"] * features["hate"]
    )
    if features["referral"]:
        score += .05
    if float(item.get("fresh_hours") or 999) < 24:
        score += .03
    return max(0.0, min(1.0, score))


def rank_feed(state: AgentState, limit: int = 20) -> AgentState:
    interests = list(dict.fromkeys([*state.user.get("interests", []), *state.interest_tags]))
    hates = list(dict.fromkeys([*state.user.get("hates", []), *state.hate_tags]))
    interaction_signal = {str(item_id): float(value) for item_id, value in (state.memory.get("interaction_signal") or {}).items()}
    hidden_item_ids = {str(item_id) for item_id in (state.memory.get("hidden_item_ids") or [])}
    learned_model = load_runtime_ranker()
    learned_jobs = learned_model is not None
    scored: list[dict[str, Any]] = []

    for item in state.candidates:
        item_id = str(item.get("id"))
        if item_id in hidden_item_ids:
            continue
        features = build_feature_vector(
            state.user,
            item,
            interest_tags=interests,
            hate_tags=hates,
            interaction_signal=interaction_signal.get(item_id, 0.0) * .1,
        )
        rule_score = _rule_score(features, item)
        model_score = None
        if learned_model is not None and item.get("type") == "job":
            model_score = learned_model.predict(features)
            final = .78 * model_score + .22 * rule_score
            # A learned model may personalize relevance, but explicit user
            # boundaries remain a hard product constraint.
            if features["hate"]:
                final = min(final, .12)
            backend = "learned-logistic+guardrails"
        else:
            final = rule_score
            backend = "hybrid-rules"
        feedback_boost = max(-.08, min(.08, interaction_signal.get(item_id, 0.0) * .01))
        final = max(0.0, min(1.0, final + feedback_boost))
        breakdown = {
            "relevance": round(features["relevance"], 3),
            "skill_overlap": round(features["skill_overlap"], 3),
            "location_match": round(features["location_match"], 3),
            "social": round(features["social"], 3),
            "freshness": round(features["freshness"], 3),
            "popularity": round(features["popularity"], 3),
            "eligibility": round(features["eligibility"], 3),
            "hate": round(features["hate"], 3),
            "referral": round(features["referral"], 3),
            "feedback": round(features["feedback"], 3),
            "rule_score": round(rule_score, 3),
            "model_score": round(model_score, 3) if model_score is not None else None,
        }
        scored.append({
            **item,
            "match_score": round(final, 4),
            "breakdown": breakdown,
            "why": _why(item, breakdown),
            "agent": "feed_ranker",
            "ranker_backend": backend,
            "model_version": learned_model.model_version if model_score is not None else "rules-v1",
        })

    scored.sort(key=lambda item: item["match_score"], reverse=True)
    selected: list[dict[str, Any]] = []
    while scored and len(selected) < limit:
        if not selected:
            selected.append(scored.pop(0))
            continue
        best_index = max(
            range(len(scored)),
            key=lambda index: .7 * scored[index]["match_score"] - .3 * max(_similarity(scored[index], previous) for previous in selected),
        )
        selected.append(scored.pop(best_index))
    state.ranked_feed = selected
    state.metadata["ranker_backend"] = "learned-logistic+guardrails" if learned_jobs else "hybrid-rules"
    state.metadata["model_version"] = learned_model.model_version if learned_model else "rules-v1"
    state.trace(
        "feed_ranker",
        "complete",
        "Learned ranking with explicit safety guardrails and MMR reranking complete" if learned_jobs else "Hybrid score + MMR reranking complete",
        returned=len(selected),
        weights=RULE_WEIGHTS,
        model_version=state.metadata["model_version"],
    )
    return state


def _why(item: dict[str, Any], breakdown: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if breakdown["skill_overlap"] >= .5:
        reasons.append("Matches skills in your twin")
    if breakdown.get("location_match", 0) > 0:
        reasons.append("Fits your location or remote preference")
    if breakdown["freshness"] >= .75:
        reasons.append("Fresh signal from the last day")
    if breakdown["social"] > 0:
        reasons.append("Your graph has a warm path")
    if breakdown.get("model_score") is not None:
        reasons.append("Personalized from learned interaction patterns")
    return reasons[:4] or ["Relevant to your current direction"]
