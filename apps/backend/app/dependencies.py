from functools import lru_cache

from .ai import AIProvider, AIProviderFactory
from .config import Settings, get_settings
from .tools.registry import ToolRegistry


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()


@lru_cache
def get_tool_registry() -> ToolRegistry:
    return ToolRegistry()


@lru_cache
def get_ai_provider() -> AIProvider:
    return AIProviderFactory.create(get_app_settings().ai_provider)
