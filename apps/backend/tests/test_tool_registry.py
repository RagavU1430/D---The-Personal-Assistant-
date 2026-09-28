import pytest
from pydantic import BaseModel

from app.tools.base import BaseTool, ToolResult
from app.tools.registry import ToolNotFoundError, ToolRegistry


class ExampleInput(BaseModel):
    value: str


class ExampleTool(BaseTool):
    name = "example"
    description = "A test tool"
    input_schema = ExampleInput

    async def execute(self, arguments: dict) -> ToolResult:
        return ToolResult(success=True, output=arguments["value"])


def test_registry_register_get_list() -> None:
    registry = ToolRegistry([ExampleTool()])
    assert registry.get("example").name == "example"
    assert [tool.name for tool in registry.list()] == ["example"]


def test_registry_rejects_duplicates_and_unknown_tools() -> None:
    registry = ToolRegistry([ExampleTool()])
    with pytest.raises(ValueError):
        registry.register(ExampleTool())
    with pytest.raises(ToolNotFoundError):
        registry.get("missing")
