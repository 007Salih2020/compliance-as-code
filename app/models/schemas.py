from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Decision = Literal["allow", "allow_with_warning", "block"]


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=20000)


class ChatRequest(BaseModel):
    team: str | None = None
    app_id: str | None = None
    model: str
    deployment_name: str
    messages: list[ChatMessage]
    max_tokens: int = Field(default=512, ge=1, le=8192)
    metadata: dict[str, str] = Field(default_factory=dict)


class EmbeddingsRequest(BaseModel):
    team: str | None = None
    app_id: str | None = None
    model: str
    deployment_name: str
    input: str = Field(min_length=1, max_length=16000)


class RuleHit(BaseModel):
    rule_id: str
    category: str
    severity: str
    match: str
    score: int


class PolicyDecision(BaseModel):
    decision: Decision
    rule_hits: list[RuleHit] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    total_score: int = 0


class UsageRecord(BaseModel):
    user_id: str
    team: str
    app_id: str
    prompt_tokens: int
    response_tokens: int
    timestamp: datetime


class QuotaStatus(BaseModel):
    allowed: bool
    reason: str | None = None
    team_usage: int = 0
    team_limit: int = 0
    user_usage: int = 0
    user_limit: int = 0


class AuditEvent(BaseModel):
    timestamp: datetime
    user_id: str
    app_id: str
    team: str
    model: str
    deployment_name: str
    prompt_hash: str
    decision: Decision
    rule_hits: list[RuleHit]
    estimated_tokens: int
    latency_ms: int
    response_status: int
    correlation_id: str
    action: str
    route: str
    warning_count: int = 0


class AdminPolicyUpdate(BaseModel):
    forbidden_code_names: list[str] | None = None
    blocked_phrases: list[str] | None = None
    warning_phrases: list[str] | None = None


class QuotaUpdate(BaseModel):
    team: str
    per_minute_limit: int = Field(ge=1)
    per_day_limit: int = Field(ge=1)


class DemoDataRequest(BaseModel):
    replace_existing: bool = True


class ModelPolicyUpdate(BaseModel):
    team: str
    allowed_models: list[str] = Field(default_factory=list)
    denied_models: list[str] = Field(default_factory=list)
