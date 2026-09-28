import logging
import sys
from typing import Any

from .config import settings


class SecretFilter(logging.Filter):
    _sensitive = ("api_key", "password", "token", "secret", "credential")

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for key in self._sensitive:
            if key in message.lower():
                record.msg = "Sensitive value omitted from log"
                record.args = ()
                break
        return True


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    handler.addFilter(SecretFilter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, message: str, **context: Any) -> None:
    safe_context = {
        key: value for key, value in context.items() if not any(word in key.lower() for word in SecretFilter._sensitive)
    }
    logger.info("%s %s", message, safe_context)
