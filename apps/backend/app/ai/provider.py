from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class AIProvider(ABC):
    name = "base"

    @abstractmethod
    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        raise NotImplementedError

    async def generate_structured(self, messages: list[dict[str, str]], response_model: type[T], **kwargs: Any) -> T:
        text = await self.generate(messages, **kwargs)
        data = text.strip()
        try:
            if data.startswith("{") or data.startswith("["):
                return response_model.model_validate_json(data)
            if data:
                return response_model.model_validate({"message": data})
        except ValidationError:
            pass
        return response_model.model_validate({"message": text})


class MockAIProvider(AIProvider):
    name = "mock"

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        last_message = messages[-1]["content"] if messages else ""
        lower = last_message.lower()

        if messages and messages[-1].get("role") == "tool":
            try:
                tool_result = json.loads(last_message)
                if tool_result.get("success"):
                    tool = tool_result.get("tool")
                    data = tool_result.get("data") or {}
                    if tool == "memory_usage":
                        return (
                            f"Memory usage is currently {data.get('percentage')}%, "
                            f"with {data.get('available')} bytes available."
                        )
                    if tool == "cpu_usage":
                        return f"CPU usage is currently {data.get('percentage')}%."
                    if tool == "current_time":
                        return f"The current local time is {data.get('formatted')} ({data.get('timezone')})."
                    if tool == "system_status":
                        return (
                            f"System status is healthy. CPU is {data.get('cpu_percentage')}% "
                            f"and memory is {data.get('memory_percentage')}%."
                        )
                    return f"{tool} completed successfully with structured data: {json.dumps(data, default=str)}"
                return f"I could not complete {tool_result.get('tool')}: {tool_result.get('message')}"
            except json.JSONDecodeError:
                pass

        if "hello" in lower or "hi" in lower:
            return "Hello. How can I help?"
        if "what can you do" in lower:
            return (
                "I can help with intent recognition, planning, safe tool suggestions, "
                "and structured guidance for development workflows."
            )
        if "open vscode" in lower or "open vs code" in lower:
            return "I understand. I can prepare a safe plan to open VS Code and then check for your project context."
        if "prepare my development environment" in lower:
            return (
                "I can help by outlining the setup steps, checking the project structure, "
                "and validating the next safe actions."
            )
        if "system" in lower or "status" in lower:
            return "I can inspect the current status and propose a safe system-check plan."
        if "debug" in lower or "error" in lower:
            return "I can break this into a clear debugging plan and validate the next safe step before execution."
        if "shell" in lower or "command" in lower:
            return (
                "I can help structure a safe command request, but I will not execute "
                "arbitrary shell commands directly."
            )
        return (
            "I understand the request and will keep the workflow structured, safe, "
            "and focused on the next valid step."
        )

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(messages, **kwargs)


class OpenAIProvider(AIProvider):
    name = "openai"

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return "OpenAI provider is configured but not actively used in this local Phase 1 mock setup."

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(messages, **kwargs)


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str = "gemini-3.8-flash", timeout: float = 12.0) -> None:
        self.api_key = api_key
        self.model = model or "gemini-3.8-flash"
        self.timeout = timeout

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        if not self.api_key:
            return "Gemini provider requires GEMINI_API_KEY."
        contents = [
            {"role": "model" if message["role"] == "assistant" else "user", "parts": [{"text": message["content"]}]}
            for message in messages
            if message["role"] != "system"
        ]
        system = next((message["content"] for message in messages if message["role"] == "system"), None)
        payload: dict[str, Any] = {"contents": contents}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, params={"key": self.api_key}, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(messages, **kwargs)


class AnthropicProvider(AIProvider):
    name = "anthropic"

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return "Anthropic provider is configured but not actively used in this local Phase 1 mock setup."

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(messages, **kwargs)


class OpenRouterProvider(AIProvider):
    name = "openrouter"

    def __init__(self, api_key: str | None = None, model: str = "openai/gpt-4o-mini", timeout: float = 12.0) -> None:
        self.api_key = api_key
        self.model = model or "openai/gpt-4o-mini"
        self.timeout = timeout

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return await self._generate_openai_compatible(
            messages,
            "https://openrouter.ai/api/v1",
            "OPENROUTER_API_KEY",
            {"HTTP-Referer": "http://127.0.0.1:8000", "X-Title": "D - The personal Assistant"},
        )

    async def _generate_openai_compatible(
        self,
        messages: list[dict[str, str]],
        base_url: str,
        key_name: str,
        extra_headers: dict[str, str] | None = None,
    ) -> str:
        if not self.api_key:
            return f"{self.name.title()} provider requires {key_name}."
        headers = {"Authorization": f"Bearer {self.api_key}", **(extra_headers or {})}
        payload = {"model": self.model, "messages": messages}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{base_url.rstrip('/')}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(messages, **kwargs)


class LocalModelProvider(AIProvider):
    name = "local"

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return "Local model provider is configured but not actively used in this local Phase 1 mock setup."

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(messages, **kwargs)


class NvidiaNimProvider(OpenRouterProvider):
    name = "nvidia_nim"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://integrate.api.nvidia.com/v1",
        model: str = "deepseek-ai/deepseek-v4.1-flash",
        timeout: float = 12.0,
    ) -> None:
        super().__init__(api_key=api_key, model=model, timeout=timeout)
        self.base_url = base_url

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return await self._generate_openai_compatible(messages, self.base_url, "NVIDIA_NIM_API_KEY")

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(messages, **kwargs)


class AIProviderFactory:
    @staticmethod
    def create(
        provider_name: str | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 12.0,
    ) -> AIProvider:
        normalized = (provider_name or "mock").lower()
        if normalized == "gemini":
            return GeminiProvider(api_key=api_key, model=model or "gemini-3.8-flash", timeout=timeout)
        if normalized == "openrouter":
            return OpenRouterProvider(api_key=api_key, model=model or "openai/gpt-4o-mini", timeout=timeout)
        if normalized in {"nvidia_nim", "nim"}:
            return NvidiaNimProvider(
                api_key=api_key,
                base_url=base_url or "https://integrate.api.nvidia.com/v1",
                model=model or "deepseek-ai/deepseek-v4.1-flash",
                timeout=timeout,
            )
        providers: dict[str, type[AIProvider]] = {
            "mock": MockAIProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "local": LocalModelProvider,
        }
        return providers.get(normalized, MockAIProvider)()


class AIProviderRouter(AIProvider):
    """Low-latency ordered failover with a short circuit cooldown per provider."""

    name = "router"

    def __init__(self, providers: list[AIProvider], cooldown_seconds: float = 30.0) -> None:
        self.providers = providers or [MockAIProvider()]
        self.cooldown_seconds = cooldown_seconds
        self._cooldown_until: dict[str, float] = {}
        self.last_provider = ""

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        last_error: Exception | None = None
        now = time.monotonic()
        for provider in self.providers:
            if self._cooldown_until.get(provider.name, 0) > now:
                continue
            try:
                response = await provider.generate(messages, **kwargs)
                self.last_provider = provider.name
                return response
            except Exception as exc:
                last_error = exc
                if self._should_cool_down(exc):
                    self._cooldown_until[provider.name] = time.monotonic() + self.cooldown_seconds
        if last_error is not None:
            raise last_error
        return await MockAIProvider().generate(messages, **kwargs)

    def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        async def one() -> AsyncIterator[str]:
            yield await self.generate(messages, **kwargs)

        return one()

    @staticmethod
    def _should_cool_down(error: Exception) -> bool:
        if isinstance(error, (httpx.TimeoutException, httpx.NetworkError, TimeoutError)):
            return True
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code == 429 or error.response.status_code >= 500
        return False
