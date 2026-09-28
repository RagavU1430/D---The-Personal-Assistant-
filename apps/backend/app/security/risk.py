from enum import StrEnum


class RiskLevel(StrEnum):
    SAFE = "safe"
    CONFIRM = "confirm"
    BLOCK = "block"
