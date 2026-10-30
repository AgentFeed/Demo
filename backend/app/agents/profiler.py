from __future__ import annotations

import re
from typing import Any

from .state import AgentState
from ..integrations.groq_client import get_groq_client


SKILL_ALIASES = {
    "react": "React", "typescript": "TypeScript", "javascript": "JavaScript", "python": "Python", "sql": "SQL",
    "node": "Node.js", "node.js": "Node.js", "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "aws": "AWS", "llm": "LLM", "rag": "RAG", "figma": "Figma", "product": "Product", "ml": "ML",
}


def extract_skills(text: str) -> list[str]:
    normalized = text.lower()
    found: list[str] = []
    for needle, label in SKILL_ALIASES.items():
        if re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", normalized) and label not in found:
            found.append(label)
    return found


def profile_resume(state: AgentState, raw_text: str | None = None, parsed: dict[str, Any] | None = None) -> AgentState:
    text = raw_text or ""
    groq = get_groq_client()
    if groq and text and not parsed:
        try:
            parsed = groq.json_completion(
                "You are the Profiler agent for Bharat Career Twin. Extract only valid JSON with name, skills, education, experience, projects, certifications, ats_score, strengths, gaps, and suggestions.",
                f"Resume text:\n{text[:20000]}",
                temperature=0.1,
                max_tokens=1400,
            )
            state.metadata["profiler_backend"] = "groq"
        except Exception as exc:
            state.metadata["profiler_backend"] = "local-fallback"
            state.metadata["profiler_error"] = str(exc)
    extracted_skills = extract_skills(text)
    base = parsed or {}
    skills = list(dict.fromkeys([*(base.get("skills") or []), *extracted_skills, *state.user.get("skills", [])]))
    gaps = [skill for skill in ["Docker", "Kubernetes", "SQL"] if skill not in skills][:3]
    ats = min(96, 60 + min(24, len(skills) * 4) + (4 if state.user.get("experience_level") else 0))
    state.resume_json = {
        "name": base.get("name") or state.user.get("full_name"),
        "skills": skills,
        "education": base.get("education") or ([state.user.get("education")] if state.user.get("education") else []),
        "experience": base.get("experience") or [],
        "projects": base.get("projects") or [],
        "certifications": base.get("certifications") or [],
        "ats_score": ats,
        "strengths": ["Skill signal is explicit", "Profile has a clear direction", "Good base for explainable matches"],
        "gaps": gaps,
        "suggestions": [f"Add {gap} with a small project" for gap in gaps] or ["Keep adding recent outcomes"],
    }
    state.trace("profiler", "complete", "Resume mapped into a structured twin", ats_score=ats, skills=skills)
    return state
