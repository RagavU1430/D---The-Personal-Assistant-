import platform
from functools import lru_cache

from .ai import AIProvider, AIProviderFactory, AIProviderRouter, MockAIProvider
from .computer.controller import ComputerController, FakeComputerController, WindowsComputerController
from .config import Settings, get_settings
from .lifecycle import DApplicationLifecycle
from .tools.computer import register_computer_tools
from .tools.registry import ToolRegistry
from .tools.system import register_system_tools


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()


@lru_cache
def get_tool_registry() -> ToolRegistry:
    registry = register_system_tools(ToolRegistry())
    return register_computer_tools(registry, get_computer_controller())


@lru_cache
def get_computer_controller() -> ComputerController:
    if platform.system() == "Windows":
        return WindowsComputerController()
    return FakeComputerController()


@lru_cache
def get_lifecycle() -> DApplicationLifecycle:
    return DApplicationLifecycle(controller=get_computer_controller())


@lru_cache
def get_ai_provider() -> AIProvider:
    app_settings = get_app_settings()
    keys = {
        "gemini": app_settings.gemini_api_key,
        "openrouter": app_settings.openrouter_api_key,
        "nvidia_nim": app_settings.nvidia_nim_api_key,
    }
    preferred = app_settings.ai_provider.lower().replace("-", "_")
    if preferred == "nim":
        preferred = "nvidia_nim"
    order = [preferred, "gemini", "openrouter", "nvidia_nim"] if preferred else ["gemini", "openrouter", "nvidia_nim"]
    providers: list[AIProvider] = []
    for name in dict.fromkeys(order):
        if keys.get(name):
            providers.append(
                AIProviderFactory.create(
                    name,
                    api_key=keys[name],
                    base_url=app_settings.nvidia_nim_base_url,
                    model=app_settings.ai_model,
                    timeout=app_settings.ai_timeout_seconds,
                )
            )
    providers.append(MockAIProvider())
    return AIProviderRouter(providers, cooldown_seconds=app_settings.provider_cooldown_seconds)
