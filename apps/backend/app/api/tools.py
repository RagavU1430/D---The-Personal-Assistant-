from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..config import settings
from ..dependencies import get_tool_registry
from ..tools.executor import ToolExecutor
from ..tools.registry import ToolRegistry

router = APIRouter(tags=["tools"])


class ToolExecutionRequest(BaseModel):
    tool: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


@router.get("/tools")
async def list_tools(registry: ToolRegistry = Depends(get_tool_registry)) -> dict[str, list[dict[str, Any]]]:
    return {"tools": [tool.metadata() for tool in registry.get_enabled_tools()]}


@router.post("/tools/execute")
async def execute_tool(
    request: ToolExecutionRequest,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> dict[str, Any]:
    executor = ToolExecutor(registry, timeout_seconds=settings.tool_timeout_seconds)
    result = await executor.execute(request.tool, request.arguments)
    return result.model_dump()