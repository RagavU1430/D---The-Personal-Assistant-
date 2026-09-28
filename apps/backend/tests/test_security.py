from app.security import PermissionDecision, PermissionEngine, RiskLevel


def test_safe_permission_is_available() -> None:
    assert PermissionEngine().evaluate(RiskLevel.SAFE) == PermissionDecision.SAFE
