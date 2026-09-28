from __future__ import annotations

import asyncio
import time
from typing import Any

from pydantic import BaseModel, ValidationError

from ..security import AuditLogger, PermissionDecision, PermissionEngine
from .base import BaseTool, ToolResult
from .registry import ToolNotFoundError, ToolRegistry


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        permission_engine: PermissionEngine | None = None,
        audit_logger: AuditLogger | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.registry = registry
        self.permission_engine = permission_engine or PermissionEngine()
        self.audit_logger = audit_logger or AuditLogger()
        self.timeout_seconds = timeout_seconds

    async def execute(self, name: str, arguments: dict[str, Any] | None = None) -> ToolResult:
        started = time.perf_counter()
        tool: BaseTool | None = None
        decision = "rejected"
        try:
            tool = self.registry.get(name)
            if not tool.enabled:
                return self._result(name, False, "TOOL_DISABLED", "This tool is disabled.", started)

            try:
                parsed_arguments: BaseModel = tool.input_schema.model_validate(arguments or {})
            except ValidationError as exc:
                return self._result(name, False, "VALIDATION_ERROR", "Invalid tool arguments.", started, str(exc))

            permission = self.permission_engine.evaluate(tool.risk_level)
            decision = permission.value
            if permission == PermissionDecision.BLOCK:
                return self._result(name, False, "BLOCKED", "This operation is prohibited.", started)
            if permission == PermissionDecision.CONFIRM:
                return self._result(
                    name,
                    False,
                    "CONFIRMATION_REQUIRED",
                    "Confirmation is required before this tool can run.",
                    started,
                    confirmation_required=True,
                )

            result = await asyncio.wait_for(tool.execute(parsed_arguments), timeout=self.timeout_seconds)
            return self._normalize(result, name, started)
        except ToolNotFoundError:
            return self._result(name, False, "TOOL_NOT_FOUND", "The requested tool is not registered.", started)
        except TimeoutError:
            return self._result(name, False, "TIMEOUT", "Tool execution exceeded its time limit.", started)
        except Exception:
            return self._result(name, False, "EXECUTION_ERROR", "The tool failed during execution.", started)
        finally:
            self.audit_logger.record(
                "tool_execution_attempt",
                tool=name,
                details={
                    "risk": tool.risk_level.value if tool else None,
                    "decision": decision,
                    "duration_ms": self._elapsed_ms(started),
                },
            )

    async def execute_plan(self, steps: list[dict[str, Any]]) -> list[ToolResult]:
        results: list[ToolResult] = []
        for step in steps:
            result = await self.execute(step["tool"], step.get("arguments", {}))
            results.append(result)
            if not result.success:
                break
        return results

    def _normalize(self, result: ToolResult, name: str, started: float) -> ToolResult:
        result.tool = name
        result.execution_time_ms = self._elapsed_ms(started)
        if not result.message:
            result.message = "Tool completed." if result.success else "Tool failed."
        self.audit_logger.record(
            "tool_execution_result",
            tool=name,
            details={
                "success": result.success,
                "error_code": result.error_code,
                "duration_ms": result.execution_time_ms,
            },
        )
        return result

    def _result(
        self,
        name: str,
        success: bool,
        error_code: str,
        message: str,
        started: float,
        details: str | None = None,
        confirmation_required: bool = False,
    ) -> ToolResult:
        result = ToolResult(
            success=success,
            tool=name,
            error_code=error_code,
            message=message,
            execution_time_ms=self._elapsed_ms(started),
        )
        if confirmation_required:
            result.data = {"status": "confirmation_required", "tool": name, "risk": "confirm"}
        self.audit_logger.record(
            "tool_execution_result",
            tool=name,
            details={
                "success": success,
                "error_code": error_code,
                "duration_ms": result.execution_time_ms,
                "detail": details,
            },
        )
        return result

    @staticmethod
    def _elapsed_ms(started: float) -> float:
        return round((time.perf_counter() - started) * 1000, 3)