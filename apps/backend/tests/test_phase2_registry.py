import pytest
from pydantic import BaseModel

from app.security import RiskLevel
from app.tools.base import BaseTool, ToolResult
from app.tools.registry import ToolRegistry


class ExampleInput(BaseModel):
    value: str


class ExampleTool(BaseTool):
    name = "example"
    description = "An example tool"
    category = "test"
    version = "1.0"
    risk_level = RiskLevel.SAFE
    input_schema = ExampleInput

    async def execute(self, arguments: ExampleInput) -> ToolResult:
        return ToolResult(success=True, tool=self.name, data={"value": arguments.value}, message="ok")


def test_registry_metadata_schema_and_enabled_tools() -> None:
    registry = ToolRegistry([ExampleTool()])

    assert registry.exists("example")
    assert registry.get_enabled_tools() == [registry.get("example")]
    assert registry.get_tool_schema("example")["type"] == "object"
    assert registry.metadata("example")["category"] == "test"


def test_registry_unregisters_and_rejects_duplicates() -> None:
    registry = ToolRegistry([ExampleTool()])
    with pytest.raises(ValueError):
        registry.register(ExampleTool())
    registry.unregister("example")
    assert not registry.exists("example")
