import pytest

from app.config import Settings
from app.tools.files import register_file_tools
from app.tools.registry import ToolRegistry


def test_recycle_bin_tool_is_confirmation_protected() -> None:
    settings = Settings(enable_file_tools=True, approved_file_roots="C:/Projects")
    registry = register_file_tools(ToolRegistry(), settings)

    tool = registry.get("move_to_recycle_bin")
    assert tool.risk_level.value == "confirm"


@pytest.mark.asyncio
async def test_recycle_bin_rejects_paths_outside_approved_roots() -> None:
    settings = Settings(enable_file_tools=True, approved_file_roots="C:/Projects")
    registry = register_file_tools(ToolRegistry(), settings)

    result = await registry.get("move_to_recycle_bin").execute({"path": "C:/Windows/system.ini"})

    assert result.success is False
    assert result.error_code == "PATH_NOT_ALLOWED"
