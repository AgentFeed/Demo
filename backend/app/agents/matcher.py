from __future__ import annotations

from .state import AgentState


def generate_candidates(state: AgentState, jobs: list[dict], schemes: list[dict], peers: list[dict], startups: list[dict]) -> AgentState:
    # The production plan uses pgvector recall. The local adapter uses the same
    # candidate boundary with deterministic lexical overlap so it works offline.
    all_items = [*jobs, *schemes, *peers, *startups]
    state.metadata.setdefault("matcher_backend", "local-lexical")
    query_terms = {value.lower() for value in [*state.user.get("skills", []), *state.interest_tags]}
    scored: list[dict] = []
    for item in all_items:
        terms = {value.lower() for value in [*(item.get("skills") or []), *(item.get("interests") or []), item.get("category", ""), item.get("name", "")]}
        overlap = len(query_terms & terms)
        scored.append({**item, "candidate_overlap": overlap})
    scored.sort(key=lambda item: (item["candidate_overlap"], item.get("fresh_hours", 999)), reverse=True)
    state.candidates = scored[:200]
    state.trace("matcher", "complete", "Candidate recall complete", candidates=len(state.candidates), backend="local lexical fallback")
    return state
