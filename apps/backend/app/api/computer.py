from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..computer.controller import ComputerController
from ..config import settings
from ..dependencies import get_computer_controller, get_lifecycle, get_tool_registry
from ..lifecycle import DApplicationLifecycle
from ..tools.executor import ToolExecutor
from ..tools.registry import ToolRegistry

router = APIRouter(tags=["computer"])


@router.get("/computer/status")
async def computer_status(lifecycle: DApplicationLifecycle = Depends(get_lifecycle)) -> dict[str, object]:
    return lifecycle.health()


@router.post("/computer/stop")
async def stop_computer(controller: ComputerController = Depends(get_computer_controller)) -> dict[str, object]:
    controller.emergency_stop()
    return {"computer_control": False, "status": "stopped"}


@router.post("/computer/resume")
async def resume_computer(controller: ComputerController = Depends(get_computer_controller)) -> dict[str, object]:
    controller.resume()
    return {"computer_control": True, "status": "resumed"}


@router.get("/windows")
async def list_windows(
    registry: ToolRegistry = Depends(get_tool_registry),
) -> dict[str, list[dict[str, Any]]]:
    result = await ToolExecutor(registry, timeout_seconds=settings.tool_timeout_seconds).execute("list_windows", {})
    return {"windows": result.data if result.success and isinstance(result.data, list) else []}


@router.get("/computer/active-window")
async def active_window(registry: ToolRegistry = Depends(get_tool_registry)) -> dict[str, Any]:
    executor = ToolExecutor(registry, timeout_seconds=settings.tool_timeout_seconds)
    result = await executor.execute("get_active_window", {})
    return {"window": result.data if result.success else None, "error_code": result.error_code}


@router.post("/computer/screenshot")
async def screenshot(registry: ToolRegistry = Depends(get_tool_registry)) -> dict[str, Any]:
    result = await ToolExecutor(registry, timeout_seconds=settings.tool_timeout_seconds).execute("take_screenshot", {})
    return result.model_dump()


@router.post("/startup")
async def set_startup(enabled: bool, lifecycle: DApplicationLifecycle = Depends(get_lifecycle)) -> dict[str, object]:
    await lifecycle.set_start_with_windows(enabled)
    return {"start_with_windows": lifecycle.startup_manager.enabled}
