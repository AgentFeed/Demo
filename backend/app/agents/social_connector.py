from __future__ import annotations

from .state import AgentState


def enrich_social(state: AgentState) -> AgentState:
    enriched: list[dict] = []
    for item in state.candidates:
        if item.get("type") == "peer":
            mutuals = int(item.get("mutual_count", 0))
            social = min(1.0, (mutuals / 5) * .5)
            enriched.append({**item, "mutual_count": mutuals, "social_score": social, "referral_path": []})
        else:
            has_referral = bool(item.get("has_referral")) or (item.get("company") == "TCS" and state.user_id == "demo_fresher")
            enriched.append({**item, "social_score": .5 if has_referral else 0, "has_referral": has_referral, "referral_path": ["You", "Priya", item.get("company")] if has_referral else []})
    state.candidates = enriched
    state.trace("social_connector", "complete", "Social proof and referral hints attached")
    return state
