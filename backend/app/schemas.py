from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class UserUpdate(BaseModel):
    full_name: str | None = None
    city: str | None = None
    state: str | None = None
    experience_level: str | None = None
    education: str | None = None
    skills: list[str] | None = None
    interests: list[str] | None = None
    hates: list[str] | None = None


class InteractionCreate(BaseModel):
    item_id: str
    item_type: Literal["job", "scheme", "peer", "startup"]
    action: Literal["like", "save", "hide", "apply", "view", "share"]
    dwell_ms: int = Field(default=0, ge=0)
    reason: str | None = None


class ImpressionCreate(BaseModel):
    item_id: str = Field(min_length=1, max_length=200)
    item_type: Literal["job", "scheme", "peer", "startup"] = "job"
    rank_position: int = Field(ge=1, le=1000)
    candidate_source: str = Field(default="feed", min_length=1, max_length=80)
    model_version: str = Field(default="rules-v1", min_length=1, max_length=80)
    surface: str = Field(default="feed", min_length=1, max_length=80)
    context: dict[str, Any] = Field(default_factory=dict)


class ImpressionBatchCreate(BaseModel):
    impressions: list[ImpressionCreate] = Field(min_length=1, max_length=100)


class StartupCreate(BaseModel):
    title: str = Field(min_length=10, max_length=140)
    description: str = Field(min_length=40, max_length=2000)
    category: str = Field(default="Community", min_length=2, max_length=60)
    skills_needed: list[str] = Field(min_length=1, max_length=12)
    location_city: str = Field(default="Nagpur", min_length=2, max_length=80)


class StartupApply(BaseModel):
    message: str = Field(min_length=10, max_length=1000)
    skill_offer: list[str] = Field(min_length=1, max_length=12)


class ConnectCreate(BaseModel):
    peer_id: str
    message: str = Field(min_length=10, max_length=1000)


class ShareCreate(BaseModel):
    item_type: str
    item_id: str


class IngestJobsCreate(BaseModel):
    csv_url: str = Field(min_length=1, max_length=2000)


class FeedResponse(BaseModel):
    items: list[dict[str, Any]]
    next_offset: int | None
    agent_trace: list[dict[str, Any]]
    steer: dict[str, Any]
