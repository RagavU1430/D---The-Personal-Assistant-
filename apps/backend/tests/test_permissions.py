import pytest

from app.security import PermissionDecision, PermissionEngine, RiskLevel


@pytest.mark.parametrize(
    ("risk", "decision"),
    [
        (RiskLevel.SAFE, PermissionDecision.SAFE),
        (RiskLevel.CONFIRM, PermissionDecision.CONFIRM),
        (RiskLevel.BLOCK, PermissionDecision.BLOCK),
    ],
)
def test_permission_decisions(risk: RiskLevel, decision: PermissionDecision) -> None:
    assert PermissionEngine().evaluate(risk) == decision
