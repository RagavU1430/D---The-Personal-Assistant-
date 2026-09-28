import pytest
from pydantic import BaseModel

from app.security import PermissionDecision, PermissionEngine, RiskLevel
from app.tools.base import BaseTool, ToolResult
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


def test_permission_engine_preserves_all_risk_decisions() -> None:
    engine = PermissionEngine()
    assert engine.evaluate(RiskLevel.SAFE) == PermissionDecision.SAFE
    assert engine.evaluate(RiskLevel.CONFIRM) == PermissionDecision.CONFIRM
    assert engine.evaluate(RiskLevel.BLOCK) == PermissionDecision.BLOCK


class AuditInput(BaseModel):
    value: str


class AuditTool(BaseTool):
    name = "audit_tool"
    description = "A tool used to verify audit timing."
    input_schema = AuditInput

    async def execute(self, arguments: AuditInput) -> ToolResult:
        return ToolResult(success=True, tool=self.name, data={"value": arguments.value}, message="ok")


class CapturingAuditLogger:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def record(self, event: str, *, tool: str | None = None, details: dict | None = None) -> None:
        self.events.append({"event": event, "tool": tool, "details": details or {}})


@pytest.mark.asyncio
async def test_executor_audits_outcome_and_duration() -> None:
    audit = CapturingAuditLogger()
    result = await ToolExecutor(ToolRegistry([AuditTool()]), audit_logger=audit).execute("audit_tool", {"value": "x"})
    assert result.success is True
    outcome = next(event for event in audit.events if event["event"] == "tool_execution_result")
    assert outcome["details"]["success"] is True
    assert outcome["details"]["duration_ms"] >= 0