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

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]

    def list(self) -> list[BaseTool]:
        return list(self._tools.values())
