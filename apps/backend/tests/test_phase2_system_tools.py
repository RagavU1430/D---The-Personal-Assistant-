import pytest

from app.tools.registry import ToolRegistry
from app.tools.system import register_system_tools


@pytest.mark.asyncio
async def test_system_tools_return_structured_real_data() -> None:
    registry = ToolRegistry()
    register_system_tools(registry)

    for name in ("system_status", "cpu_usage", "memory_usage", "disk_usage", "current_time", "jarvis_health"):
        result = await registry.get(name).execute(registry.get(name).input_schema())
        assert result.success is True
        assert result.tool == name
        assert result.data is not None

    assert "python_version" in (await registry.get("system_status").execute({})).data
    assert "percentage" in (await registry.get("memory_usage").execute({})).data
