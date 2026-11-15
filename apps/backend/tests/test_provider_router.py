import httpx
import pytest

from app.ai.provider import AIProvider, AIProviderRouter


class FailingProvider(AIProvider):
    name = "limited"

    async def generate(self, messages: list[dict[str, str]], **kwargs: object) -> str:
        request = httpx.Request("POST", "https://provider.test")
        response = httpx.Response(429, request=request)
        raise httpx.HTTPStatusError("rate limited", request=request, response=response)

    def stream(self, messages: list[dict[str, str]], **kwargs: object):
        raise NotImplementedError


class HealthyProvider(AIProvider):
    name = "healthy"

    async def generate(self, messages: list[dict[str, str]], **kwargs: object) -> str:
        return "fallback response"

    def stream(self, messages: list[dict[str, str]], **kwargs: object):
        raise NotImplementedError


class ModelProvider(AIProvider):
    name = "gemini"

    def __init__(self, model: str, calls: list[str]) -> None:
        self.model = model
        self.calls = calls

    async def generate(self, messages: list[dict[str, str]], **kwargs: object) -> str:
        self.calls.append(self.model)
        if self.model == "limited-model":
            request = httpx.Request("POST", "https://provider.test")
            response = httpx.Response(429, request=request)
            raise httpx.HTTPStatusError("rate limited", request=request, response=response)
        return self.model

    def stream(self, messages: list[dict[str, str]], **kwargs: object):
        raise NotImplementedError


@pytest.mark.asyncio
async def test_router_switches_after_rate_limit_and_remembers_cooldown() -> None:
    router = AIProviderRouter([FailingProvider(), HealthyProvider()], cooldown_seconds=60)

    first = await router.generate([{"role": "user", "content": "hello"}])
    second = await router.generate([{"role": "user", "content": "hello again"}])

    assert first == "fallback response"
    assert second == "fallback response"
    assert router.last_provider.startswith("healthy")
    assert any(key.startswith("limited:") for key in router._cooldown_until)


@pytest.mark.asyncio
async def test_router_switches_models_under_the_same_provider_key() -> None:
    calls: list[str] = []
    router = AIProviderRouter(
        [ModelProvider("limited-model", calls), ModelProvider("healthy-model", calls)],
        cooldown_seconds=60,
    )

    response = await router.generate([{"role": "user", "content": "hello"}])

    assert response == "healthy-model"
    assert calls == ["limited-model", "healthy-model"]