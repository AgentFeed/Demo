from __future__ import annotations

from typing import Any

from .agents.graph import run_agent_graph
from .agents.state import AgentState
from .integrations.embeddings import get_embedding_provider
from .store import Store


def build_feed(store: Store, user_id: str, offset: int = 0, limit: int = 20, item_type: str = "all", steer: str | None = None) -> dict[str, Any]:
    user = store.get_user(user_id)
    if steer:
        store.set_memory(user_id, "steer", steer)
    memory = store.get_memory(user_id)
    effective_user = {**user}
    if memory.get("steer"):
        effective_user["steer"] = memory["steer"]
    provider = get_embedding_provider()
    query_embedding = None
    if provider.available:
        try:
            query_embedding = provider.embed_text(" ".join([*user.get("skills", []), *user.get("interests", []), memory.get("steer") or ""]))
        except Exception:
            query_embedding = None
    pool = store.candidate_pool(user_id, query_embedding=query_embedding, limit=max(200, offset + limit))
    state = AgentState(
        user_id=user_id,
        user=effective_user,
        interest_tags=user.get("interests", []),
        hate_tags=user.get("hates", []),
        memory=memory,
        interest_embedding=query_embedding,
        metadata={"candidate_backend": "pgvector" if store.__class__.__name__ == "SupabaseStore" and query_embedding and getattr(store, "last_vector_error", None) is None else "local-fallback"},
    )
    graph = run_agent_graph(state, pool["jobs"], pool["schemes"], pool["peers"], pool["startups"], store.list_interactions(user_id), limit=max(50, offset + limit))
    items = graph.ranked_feed
    if item_type != "all":
        items = [item for item in items if item.get("type") == item_type]
    page = items[offset: offset + limit]
    return {
        "items": page,
        "next_offset": offset + limit if offset + limit < len(items) else None,
        "agent_trace": graph.agent_trace,
        "steer": {"value": memory.get("steer") or "", "memory_key": "steer", "editable": True},
        "backends": graph.metadata,
    }


def explain_item(store: Store, user_id: str, item_id: str, item_type: str | None = None) -> dict[str, Any]:
    feed = build_feed(store, user_id, limit=100)
    for item in feed["items"]:
        if item.get("id") == item_id and (item_type is None or item.get("type") == item_type):
            return {"item": item, "breakdown": item.get("breakdown", {}), "why": item.get("why", []), "gap_info": item.get("gap_info", {})}
    raise KeyError(item_id)
