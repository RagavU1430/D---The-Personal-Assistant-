from abc import ABC, abstractmethod
from typing import Any


class MemoryRepository(ABC):
    @abstractmethod
    async def remember(self, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search(self, query: str) -> list[Any]:
        raise NotImplementedError
