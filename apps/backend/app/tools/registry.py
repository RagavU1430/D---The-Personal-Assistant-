from __future__ import annotations

from builtins import list as builtins_list
from collections.abc import Iterable

from .base import BaseTool


class ToolNotFoundError(KeyError):
    pass


class ToolRegistry:
    def __init__(self, tools: Iterable[BaseTool] | None = None):
        self._tools: dict[str, BaseTool] = {}
        for tool in tools or ():
            self.register(tool)

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        if name not in self._tools:
            raise ToolNotFoundError(name)
        del self._tools[name]

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]

    def list(self) -> builtins_list[BaseTool]:
        return list(self._tools.values())

    def exists(self, name: str) -> bool:
        return name in self._tools

    def get_enabled_tools(self) -> builtins_list[BaseTool]:
        return [tool for tool in self._tools.values() if tool.enabled]

    def get_tool_schema(self, name: str) -> dict:
        return self.get(name).get_schema()

    def metadata(self, name: str) -> dict:
        return self.get(name).metadata()
