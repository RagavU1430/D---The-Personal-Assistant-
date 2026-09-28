from __future__ import annotations

import platform
from datetime import datetime
from pathlib import Path

import psutil
from pydantic import BaseModel, Field

from ..ai.provider import AIProviderFactory
from ..config import settings
from ..db.database import engine
from ..security import RiskLevel
from .base import BaseTool, ToolResult
from .registry import ToolRegistry


class EmptyInput(BaseModel):
    pass


class DiskInput(BaseModel):
    path: str | None = Field(default=None, description="Optional approved path to inspect")


class SystemStatusTool(BaseTool):
    name = "system_status"
    description = "Returns safe, read-only system information."
    category = "system"
    input_schema = EmptyInput
    risk_level = RiskLevel.SAFE

    async def execute(self, arguments: EmptyInput) -> ToolResult:
        return ToolResult(
            success=True,
            tool=self.name,
            data={
                "os": platform.system(),
                "os_version": platform.release(),
                "hostname": platform.node(),
                "cpu_percentage": psutil.cpu_percent(interval=0.05),
                "memory_percentage": psutil.virtual_memory().percent,
                "disk_percentage": psutil.disk_usage(Path.cwd().anchor).percent,
                "python_version": platform.python_version(),
                "application_version": settings.app_version,
            },
            message="System status collected.",
        )


class CpuUsageTool(BaseTool):
    name = "cpu_usage"
    description = "Returns current CPU utilization."
    category = "system"
    input_schema = EmptyInput
    risk_level = RiskLevel.SAFE

    async def execute(self, arguments: EmptyInput) -> ToolResult:
        return ToolResult(
            success=True,
            tool=self.name,
            data={"percentage": psutil.cpu_percent(interval=0.05)},
            message="CPU usage collected.",
        )


class MemoryUsageTool(BaseTool):
    name = "memory_usage"
    description = "Returns current memory totals and utilization."
    category = "system"
    input_schema = EmptyInput
    risk_level = RiskLevel.SAFE

    async def execute(self, arguments: EmptyInput) -> ToolResult:
        memory = psutil.virtual_memory()
        return ToolResult(
            success=True,
            tool=self.name,
            data={
                "total": memory.total,
                "used": memory.used,
                "available": memory.available,
                "percentage": memory.percent,
            },
            message="Memory usage collected.",
        )


class DiskUsageTool(BaseTool):
    name = "disk_usage"
    description = "Returns disk usage for the approved application path."
    category = "system"
    input_schema = DiskInput
    risk_level = RiskLevel.SAFE

    async def execute(self, arguments: DiskInput) -> ToolResult:
        approved_root = Path.cwd().anchor
        requested = Path(arguments.path or approved_root).resolve()
        if requested.anchor != approved_root:
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="PATH_NOT_ALLOWED",
                message="The requested path is outside the approved system path.",
            )
        disk = psutil.disk_usage(str(requested))
        return ToolResult(
            success=True,
            tool=self.name,
            data={
                "path": str(requested),
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percentage": disk.percent,
            },
            message="Disk usage collected.",
        )


class CurrentTimeTool(BaseTool):
    name = "current_time"
    description = "Returns the local system time."
    category = "system"
    input_schema = EmptyInput
    risk_level = RiskLevel.SAFE

    async def execute(self, arguments: EmptyInput) -> ToolResult:
        now = datetime.now().astimezone()
        return ToolResult(
            success=True,
            tool=self.name,
            data={"iso": now.isoformat(), "timezone": str(now.tzinfo), "formatted": now.strftime("%Y-%m-%d %H:%M:%S")},
            message="Current time collected.",
        )


class JarvisHealthTool(BaseTool):
    name = "jarvis_health"
    description = "Returns backend, database, AI provider, and tool registry health."
    category = "system"
    input_schema = EmptyInput
    risk_level = RiskLevel.SAFE

    async def execute(self, arguments: EmptyInput) -> ToolResult:
        database_status = "ok"
        try:
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
        except Exception:
            database_status = "error"
        return ToolResult(
            success=True,
            tool=self.name,
            data={
                "backend_status": "ok",
                "database_status": database_status,
                "ai_provider_status": AIProviderFactory.create(settings.ai_provider).name,
                "tool_registry_status": "ok",
            },
            message="JARVIS health collected.",
        )


def register_system_tools(registry: ToolRegistry) -> ToolRegistry:
    if settings.enable_system_tools:
        tools = (
            SystemStatusTool(),
            CpuUsageTool(),
            MemoryUsageTool(),
            DiskUsageTool(),
            CurrentTimeTool(),
            JarvisHealthTool(),
        )
        for tool in tools:
            registry.register(tool)
    return registry
