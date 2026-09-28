import asyncio

import pytest
from pydantic import BaseModel

from app.security import RiskLevel
from app.tools.base import BaseTool, ToolResult
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class ValueInput(BaseModel):
    value: str


class SafeTool(BaseTool):
    name = "safe_tool"
    description = "Returns a value"
    category = "test"
    input_schema = ValueInput

    async def execute(self, arguments: ValueInput) -> ToolResult:
        return ToolResult(success=True, tool=self.name, data={"value": arguments.value}, message="done")


class ConfirmTool(SafeTool):
    name = "confirm_tool"
    risk_level = RiskLevel.CONFIRM


class BlockedTool(SafeTool):
    name = "blocked_tool"
    risk_level = RiskLevel.BLOCK


class FailingTool(SafeTool):
    name = "failing_tool"

    async def execute(self, arguments: ValueInput) -> ToolResult:
        raise RuntimeError("boom")


class SlowTool(SafeTool):
    name = "slow_tool"

    async def execute(self, arguments: ValueInput) -> ToolResult:
        await asyncio.sleep(0.05)
        return ToolResult(success=True, tool=self.name, data={}, message="done")


def executor(*tools: BaseTool, timeout: float = 1.0) -> ToolExecutor:
    return ToolExecutor(ToolRegistry(tools), timeout_seconds=timeout)


@pytest.mark.asyncio
async def test_executor_validates_and_executes_safe_tool() -> None:
    result = await executor(SafeTool()).execute("safe_tool", {"value": "ok"})
    assert result.success is True
    assert result.data == {"value": "ok"}
    assert result.execution_time_ms >= 0


@pytest.mark.asyncio
async def test_executor_rejects_unknown_and_invalid_arguments() -> None:
    unknown = await executor().execute("missing", {})
    invalid = await executor(SafeTool()).execute("safe_tool", {"invalid": True})
    assert unknown.error_code == "TOOL_NOT_FOUND"
    assert invalid.error_code == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_executor_requires_confirmation_and_blocks() -> None:
    confirmation = await executor(ConfirmTool()).execute("confirm_tool", {"value": "x"})
    blocked = await executor(BlockedTool()).execute("blocked_tool", {"value": "x"})
    assert confirmation.error_code == "CONFIRMATION_REQUIRED"
    assert blocked.error_code == "BLOCKED"


@pytest.mark.asyncio
async def test_executor_normalizes_failures_and_timeouts() -> None:
    failure = await executor(FailingTool()).execute("failing_tool", {"value": "x"})
    timeout = await executor(SlowTool(), timeout=0.001).execute("slow_tool", {"value": "x"})
    assert failure.error_code == "EXECUTION_ERROR"
    assert timeout.error_code == "TIMEOUT"
