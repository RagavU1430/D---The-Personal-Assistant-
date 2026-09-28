from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel

from ..security.risk import RiskLevel


class ToolResult(BaseModel):
    success: bool
    tool: str = ""
    data: Any = None
    output: Any = None
    error_code: str | None = None
    message: str = ""
    execution_time_ms: float = 0.0

    @property
    def error(self) -> str | None:
        return self.message if not self.success else None


class BaseTool(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    category: ClassVar[str] = "general"
    version: ClassVar[str] = "1.0"
    risk_level: ClassVar[RiskLevel] = RiskLevel.SAFE
    enabled: ClassVar[bool] = True
    input_schema: ClassVar[type[BaseModel]] = BaseModel

    @classmethod
    def get_schema(cls) -> dict[str, Any]:
        return cls.input_schema.model_json_schema()

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "risk": self.risk_level.value,
            "enabled": self.enabled,
        }

    @abstractmethod
    async def execute(self, arguments: Any) -> ToolResult:
        """Execute a validated request."""
