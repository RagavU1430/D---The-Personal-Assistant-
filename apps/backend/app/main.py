from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from .api.errors import unhandled_exception_handler, validation_exception_handler
from .api.health import router as health_router
from .config import settings
from .db import init_db
from .logging import configure_logging, get_logger, log_event

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    init_db()
    log_event(
        logger,
        "JARVIS-X backend started",
        environment=settings.app_env,
        version=settings.app_version,
    )
    yield
    log_event(logger, "JARVIS-X backend stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Personal AI Operating Assistant foundation",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(health_router, prefix="/api/v1")
