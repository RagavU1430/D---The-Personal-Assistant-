from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    id: str
    description: str
    action_type: Literal["reason", "tool", "respond", "confirm"] = "tool"
    tool: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentPlan(BaseModel):
    goal: str
    steps: list[PlanStep] = Field(default_factory=list)


class AssistantResponse(BaseModel):
    message: str
    intent: str = "GENERAL_CHAT"
    requires_action: bool = False
    plan: AgentPlan | None = None
