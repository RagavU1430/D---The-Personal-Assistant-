from abc import ABC, abstractmethod
from typing import Any


class AgentOrchestrator(ABC):
    @abstractmethod
    async def run(self, request: str) -> Any:
        raise NotImplementedError


class Planner(ABC):
    @abstractmethod
    async def plan(self, request: str) -> Any:
        raise NotImplementedError


class Executor(ABC):
    @abstractmethod
    async def execute(self, plan: Any) -> Any:
        raise NotImplementedError


class Observer(ABC):
    @abstractmethod
    async def observe(self, state: Any) -> Any:
        raise NotImplementedError


class Verifier(ABC):
    @abstractmethod
    async def verify(self, result: Any) -> bool:
        raise NotImplementedError
