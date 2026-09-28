from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel

from ..security.risk import RiskLevel


class ToolResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None


class BaseTool(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    risk_level: ClassVar[RiskLevel] = RiskLevel.SAFE
    input_schema: ClassVar[type[BaseModel]] = BaseModel

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Execute a validated request."""
