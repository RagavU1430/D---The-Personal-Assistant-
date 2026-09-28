from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return "AI provider is not configured."

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(messages, **kwargs)


class AIProviderFactory:
    @staticmethod
    def create(_: str | None = None) -> AIProvider:
        return MockAIProvider()
