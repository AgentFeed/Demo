from __future__ import annotations

from collections import Counter
from typing import Any

from .state import AgentState
from ..integrations.embeddings import get_embedding_provider


ACTION_WEIGHTS = {"like": 2, "save": 3, "apply": 5, "view": 1, "hide": -5}


def mine_interests(state: AgentState, interactions: list[dict[str, Any]]) -> AgentState:
    interests = list(dict.fromkeys([*state.user.get("interests", []), *state.interest_tags]))
    hates = list(dict.fromkeys([*state.user.get("hates", []), *state.hate_tags]))
    signals = Counter()
    hidden_item_ids: list[str] = []
    for interaction in interactions:
        action = interaction.get("action")
        item_id = str(interaction.get("item_id") or "")
        signals[item_id] += ACTION_WEIGHTS.get(str(action), 0)
        if action == "hide" and interaction.get("reason"):
            hates.append(interaction["reason"])
        if action == "hide" and item_id:
            hidden_item_ids.append(item_id)
    state.interest_tags = list(dict.fromkeys(interests))
    state.hate_tags = list(dict.fromkeys(hates))
    state.memory["interaction_signal"] = dict(signals)
    state.memory["hidden_item_ids"] = list(dict.fromkeys(hidden_item_ids))
    provider = get_embedding_provider()
    if provider.available:
        try:
            state.interest_embedding = provider.embed_text(" ".join(state.interest_tags))
            state.hate_embedding = provider.embed_text(" ".join(state.hate_tags))
            state.metadata["interest_backend"] = "embedding"
        except Exception as exc:
            state.metadata["interest_backend"] = "tag-fallback"
            state.metadata["interest_error"] = str(exc)
    state.trace("interest_miner", "complete", "Interest and hate memory refreshed", interests=state.interest_tags, hates=state.hate_tags)
    return state
