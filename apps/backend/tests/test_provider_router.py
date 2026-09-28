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


@pytest.mark.asyncio
async def test_router_switches_after_rate_limit_and_remembers_cooldown() -> None:
    router = AIProviderRouter([FailingProvider(), HealthyProvider()], cooldown_seconds=60)

    first = await router.generate([{"role": "user", "content": "hello"}])
    second = await router.generate([{"role": "user", "content": "hello again"}])

    assert first == "fallback response"
    assert second == "fallback response"
    assert router.last_provider == "healthy"
    assert router._cooldown_until["limited"] > 0