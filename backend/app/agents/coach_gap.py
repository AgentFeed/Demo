from __future__ import annotations

from .state import AgentState
from ..integrations.groq_client import get_groq_client


def attach_gap_coach(state: AgentState) -> AgentState:
    current_skills = {skill.lower() for skill in state.user.get("skills", [])}
    groq = get_groq_client()
    coach_calls = 0
    enriched: list[dict] = []
    for item in state.candidates:
        required = {skill.lower() for skill in item.get("skills", [])}
        missing = [skill for skill in item.get("skills", []) if skill.lower() not in current_skills][:2]
        roadmap = [{"skill": skill, "course": "SWAYAM / NPTEL starter path", "weeks": 2} for skill in missing]
        if groq and missing and coach_calls < 2:
            try:
                coach_calls += 1
                coached = groq.json_completion(
                    "You are the Coach Gap agent. Return JSON with a roadmap array. Each roadmap entry must contain skill, course, and weeks. Only recommend free learning paths such as SWAYAM, NPTEL, or official documentation.",
                    f"User skills: {sorted(current_skills)}\nMissing skills: {missing}\nRole: {item.get('title') or item.get('name')}",
                    temperature=0.2,
                    max_tokens=500,
                )
                if isinstance(coached.get("roadmap"), list) and coached["roadmap"]:
                    roadmap = coached["roadmap"][:4]
                    state.metadata["coach_backend"] = "groq"
            except Exception as exc:
                state.metadata.setdefault("coach_backend", "local-fallback")
                state.metadata.setdefault("coach_error", str(exc))
        enriched.append({**item, "gap_info": {"missing_skills": missing, "counterfactual": "82→94% if Docker is added" if "docker" in required else None, "roadmap": roadmap}})
    state.metadata["coach_calls"] = coach_calls
    state.candidates = enriched
    state.trace("coach_gap", "complete", "Skill gaps and free-roadmap hints attached")
    return state
