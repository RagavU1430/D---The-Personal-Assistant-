from abc import ABC, abstractmethod


class SpeechToText(ABC):
    @abstractmethod
    async def transcribe(self, audio: bytes) -> str:
        raise NotImplementedError


class TextToSpeech(ABC):
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        raise NotImplementedError
