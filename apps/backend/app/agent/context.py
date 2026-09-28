from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

Role = Literal["system", "user", "assistant", "tool"]


@dataclass(slots=True)
class ChatMessage:
    role: Role
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    conversation_id: str | None = None
    message_id: str = field(default_factory=lambda: str(uuid4()))
    tool_name: str | None = None


class ConversationManager:
    def __init__(self, max_messages: int = 50) -> None:
        self.max_messages = max_messages
        self._conversations: dict[str, list[ChatMessage]] = {}

    def create_conversation(self) -> str:
        conversation_id = str(uuid4())
        self._conversations[conversation_id] = []
        return conversation_id

    def add_message(self, conversation_id: str, message: ChatMessage) -> ChatMessage:
        self._conversations.setdefault(conversation_id, [])
        self._conversations[conversation_id].append(message)
        self.truncate_context(conversation_id)
        return message

    def get_messages(self, conversation_id: str) -> list[ChatMessage]:
        return list(self._conversations.get(conversation_id, []))

    def truncate_context(self, conversation_id: str) -> None:
        messages = self._conversations.get(conversation_id, [])
        if len(messages) > self.max_messages:
            self._conversations[conversation_id] = messages[-self.max_messages :]

    def clear(self, conversation_id: str) -> None:
        self._conversations[conversation_id] = []

    def to_prompt_messages(self, conversation_id: str, *, prepend_system: str | None = None) -> list[dict[str, str]]:
        messages = self.get_messages(conversation_id)
        prompt_messages: list[dict[str, str]] = []
        if prepend_system is not None:
            prompt_messages.append({"role": "system", "content": prepend_system})
        for message in messages:
            prompt_messages.append({"role": message.role, "content": message.content})
        return prompt_messages
