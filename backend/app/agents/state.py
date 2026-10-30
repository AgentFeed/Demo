from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    user_id: str
    user: dict[str, Any]
    resume_json: dict[str, Any] | None = None
    interest_tags: list[str] = field(default_factory=list)
    hate_tags: list[str] = field(default_factory=list)
    memory: dict[str, Any] = field(default_factory=dict)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    ranked_feed: list[dict[str, Any]] = field(default_factory=list)
    agent_trace: list[dict[str, Any]] = field(default_factory=list)
    interest_embedding: list[float] | None = None
    hate_embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def trace(self, agent: str, status: str, detail: str, **data: Any) -> None:
        self.agent_trace.append({"agent": agent, "status": status, "detail": detail, **data})
