from app.ai.provider import AIProviderFactory, GeminiProvider, NvidiaNimProvider, OpenRouterProvider


def test_supported_provider_names_receive_credentials_without_logging_them() -> None:
    gemini = AIProviderFactory.create("gemini", api_key="gemini-secret")
    openrouter = AIProviderFactory.create("openrouter", api_key="router-secret")
    nim = AIProviderFactory.create("nvidia_nim", api_key="nim-secret", model="meta/test")

    assert isinstance(gemini, GeminiProvider)
    assert gemini.api_key == "gemini-secret"
    assert isinstance(openrouter, OpenRouterProvider)
    assert openrouter.api_key == "router-secret"
    assert isinstance(nim, NvidiaNimProvider)
    assert nim.api_key == "nim-secret"


def test_provider_without_key_returns_safe_configuration_message() -> None:
    provider = AIProviderFactory.create("openrouter")
    assert provider.api_key is None