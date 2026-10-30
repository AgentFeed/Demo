from __future__ import annotations

from .coach_gap import attach_gap_coach
from .interest_miner import mine_interests
from .matcher import generate_candidates
from .profiler import profile_resume
from .ranker import rank_feed
from .social_connector import enrich_social
from .state import AgentState


def _node(function):
    def run(value):
        state = value["state"]
        function(state)
        return {"state": state}

    return run


def _run_sequential(state: AgentState, jobs: list[dict], schemes: list[dict], peers: list[dict], startups: list[dict], interactions: list[dict], limit: int, raw_resume: str | None = None, parsed_resume: dict | None = None) -> AgentState:
    profile_resume(state, raw_text=raw_resume, parsed=parsed_resume)
    mine_interests(state, interactions)
    generate_candidates(state, jobs, schemes, peers, startups)
    enrich_social(state)
    attach_gap_coach(state)
    rank_feed(state, limit=limit)
    return state


def run_agent_graph(state: AgentState, jobs: list[dict], schemes: list[dict], peers: list[dict], startups: list[dict], interactions: list[dict], limit: int = 20, raw_resume: str | None = None, parsed_resume: dict | None = None) -> AgentState:
    try:
        from ..config import settings

        if not settings.use_langgraph:
            return _run_sequential(state, jobs, schemes, peers, startups, interactions, limit, raw_resume, parsed_resume)
        from langgraph.graph import END, START, StateGraph

        graph = StateGraph(dict)
        graph.add_node("profiler", lambda value: {"state": profile_resume(value["state"], raw_text=raw_resume, parsed=parsed_resume)})
        graph.add_node("interest_miner", lambda value: {"state": mine_interests(value["state"], interactions)})
        graph.add_node("matcher", lambda value: {"state": generate_candidates(value["state"], jobs, schemes, peers, startups)})
        graph.add_node("social_connector", lambda value: {"state": enrich_social(value["state"])})
        graph.add_node("coach_gap", lambda value: {"state": attach_gap_coach(value["state"])})
        graph.add_node("feed_ranker", lambda value: {"state": rank_feed(value["state"], limit=limit)})
        graph.add_edge(START, "profiler")
        graph.add_edge("profiler", "interest_miner")
        graph.add_edge("interest_miner", "matcher")
        graph.add_edge("matcher", "social_connector")
        graph.add_edge("social_connector", "coach_gap")
        graph.add_edge("coach_gap", "feed_ranker")
        graph.add_edge("feed_ranker", END)
        compiled = graph.compile()
        result = compiled.invoke({"state": state})
        completed = result.get("state") if isinstance(result, dict) else None
        if isinstance(completed, AgentState):
            completed.metadata["orchestrator_backend"] = "langgraph"
            return completed
    except Exception as exc:
        state.metadata["orchestrator_backend"] = "sequential-fallback"
        state.metadata["orchestrator_error"] = str(exc)
    return _run_sequential(state, jobs, schemes, peers, startups, interactions, limit, raw_resume, parsed_resume)
