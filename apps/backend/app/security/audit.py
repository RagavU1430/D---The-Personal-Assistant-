import logging
from typing import Any

logger = logging.getLogger(__name__)


class AuditLogger:
    def record(self, event: str, *, tool: str | None = None, details: dict[str, Any] | None = None) -> None:
        sensitive_words = ("key", "token", "password", "secret")
        safe = {
            key: "[REDACTED]" if any(word in key.lower() for word in sensitive_words) else value
            for key, value in (details or {}).items()
        }
        logger.info("audit event=%s tool=%s details=%s", event, tool or "-", safe)
