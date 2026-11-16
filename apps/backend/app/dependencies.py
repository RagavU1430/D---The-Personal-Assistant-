import platform
from functools import lru_cache

from .ai import AIProvider, AIProviderFactory, AIProviderRouter, MockAIProvider
from .computer.controller import ComputerController, FakeComputerController, WindowsComputerController
from .config import Settings, get_settings
from .lifecycle import DApplicationLifecycle
from .tools.computer import register_computer_tools
from .tools.files import register_file_tools
from .tools.registry import ToolRegistry
from .tools.system import register_system_tools


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()


@lru_cache
def get_tool_registry() -> ToolRegistry:
    registry = register_system_tools(ToolRegistry())
    registry = register_computer_tools(registry, get_computer_controller())
    return register_file_tools(registry, get_app_settings())


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
    configured_models = [model.strip() for model in app_settings.ai_models.split(",") if model.strip()]
    if not configured_models and app_settings.ai_model.strip():
        configured_models = [app_settings.ai_model.strip()]
    providers: list[AIProvider] = []
    for name in dict.fromkeys(order):
        if keys.get(name):
            models = configured_models if name == preferred and configured_models else [""]
            for model in models:
                providers.append(
                    AIProviderFactory.create(
                        name,
                        api_key=keys[name],
                        base_url=app_settings.nvidia_nim_base_url,
                        model=model,
                        timeout=app_settings.ai_timeout_seconds,
                    )
                )

    # Add custom OpenAI-compatible providers from config
    # Format: "name1=base_url1,api_key1,model1|name2=base_url2,api_key2,model2"
    if app_settings.custom_ai_providers.strip():
        for provider_spec in app_settings.custom_ai_providers.split("|"):
            provider_spec = provider_spec.strip()
            if not provider_spec:
                continue
            parts = provider_spec.split("=", 1)
            if len(parts) != 2:
                continue
            custom_name = parts[0].strip()
            config_parts = [p.strip() for p in parts[1].split(",")]
            if len(config_parts) < 1:
                continue
            base_url = config_parts[0]
            api_key = config_parts[1] if len(config_parts) > 1 and config_parts[1] else None
            model = config_parts[2] if len(config_parts) > 2 and config_parts[2] else None
            providers.append(
                AIProviderFactory.create_custom(
                    name=custom_name,
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    timeout=app_settings.ai_timeout_seconds,
                )
            )

    providers.append(MockAIProvider())
    return AIProviderRouter(providers, cooldown_seconds=app_settings.provider_cooldown_seconds)
