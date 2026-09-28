from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.agent.intents import detect_intent
from app.agent.planner import Planner
from app.ai.provider import AIProvider
from app.config import settings
from app.dependencies import get_ai_provider, get_tool_registry
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    message: str
    state: str
    plan: dict | None = None
    intent: str | None = None
    tool_results: list[dict] = Field(default_factory=list)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    registry: ToolRegistry = Depends(get_tool_registry),
    provider: AIProvider = Depends(get_ai_provider),
) -> ChatResponse:
    user_message = request.message.strip()
    planner = Planner(registry)
    plan = planner.plan(user_message)

    try:
        planner.validate_plan(plan)
    except ValueError:
        plan = planner.create_plan(user_message)

    tool_results: list[dict] = []
    state = "COMPLETED"
    if plan.steps and plan.steps[0].action_type == "tool" and plan.steps[0].tool:
        result = await ToolExecutor(registry, timeout_seconds=settings.tool_timeout_seconds).execute(
            plan.steps[0].tool,
            plan.steps[0].arguments,
        )
        tool_results.append(result.model_dump())
        if result.error_code == "CONFIRMATION_REQUIRED":
            state = "WAITING_CONFIRMATION"
        elif not result.success:
            state = "FAILED"

    messages = [{"role": "user", "content": user_message}]
    if tool_results:
        messages.append({"role": "tool", "content": json.dumps(tool_results[-1], default=str)})
    assistant_message = await provider.generate(messages)

    return ChatResponse(
        message=assistant_message,
        state=state,
        plan=plan.model_dump() if plan.steps else None,
        intent=detect_intent(user_message).value,
        tool_results=tool_results,
    )