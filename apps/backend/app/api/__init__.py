from .chat import router as chat_router
from .computer import router as computer_router
from .health import router as health_router
from .tools import router as tools_router

__all__ = ["health_router", "chat_router", "tools_router", "computer_router"]
