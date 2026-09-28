from app.agent.context import ChatMessage, ConversationManager


def test_create_message_and_truncate_context() -> None:
    manager = ConversationManager(max_messages=2)
    conversation_id = manager.create_conversation()

    manager.add_message(conversation_id, ChatMessage(role="user", content="Hello Jarvis"))
    manager.add_message(conversation_id, ChatMessage(role="assistant", content="Hello. How can I help?"))
    manager.add_message(conversation_id, ChatMessage(role="user", content="Open VS Code."))

    messages = manager.get_messages(conversation_id)
    assert len(messages) == 2
    assert messages[-1].content == "Open VS Code."


def test_clear_conversation() -> None:
    manager = ConversationManager()
    conversation_id = manager.create_conversation()
    manager.add_message(conversation_id, ChatMessage(role="user", content="hello"))

    manager.clear(conversation_id)

    assert manager.get_messages(conversation_id) == []
