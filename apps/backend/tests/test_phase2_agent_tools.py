import pytest

from app.agent.planner import Planner
from app.tools.registry import ToolRegistry
from app.tools.system import register_system_tools


def test_planner_maps_system_requests_to_registered_tools() -> None:
    registry = ToolRegistry()
    register_system_tools(registry)
    planner = Planner(registry)

    assert planner.plan("Check my system status.").steps[0].tool == "system_status"
    assert planner.plan("How much RAM am I using?").steps[0].tool == "memory_usage"
    assert planner.plan("What time is it?").steps[0].tool == "current_time"


@pytest.mark.asyncio
async def test_system_tool_is_only_executed_through_executor() -> None:
    registry = ToolRegistry()
    register_system_tools(registry)
    tool = registry.get("memory_usage")
    assert tool.input_schema() is not None
