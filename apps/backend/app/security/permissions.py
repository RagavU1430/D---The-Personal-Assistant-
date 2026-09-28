from enum import StrEnum

from .risk import RiskLevel


class PermissionDecision(StrEnum):
    SAFE = "safe"
    CONFIRM = "confirm"
    BLOCK = "block"


class PermissionEngine:
    def evaluate(self, risk: RiskLevel) -> PermissionDecision:
        return PermissionDecision(risk.value)
