import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _error(code: str, message: str, details: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


async def validation_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    validation_error = exc
    if not isinstance(validation_error, RequestValidationError):
        return JSONResponse(status_code=422, content=_error("VALIDATION_ERROR", "Request validation failed."))
    return JSONResponse(
        status_code=422,
        content=_error("VALIDATION_ERROR", "Request validation failed.", validation_error.errors()),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled application error: %s", exc.__class__.__name__)
    return JSONResponse(status_code=500, content=_error("INTERNAL_ERROR", "An unexpected error occurred."))
