from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.agent.intents import Intent, detect_intent
from app.agent.planner import Planner
from app.ai.provider import MockAIProvider
from app.api.chat import ChatRequest, chat
from app.config import Settings
from app.tools.files import register_file_tools
from app.tools.registry import ToolRegistry


def test_file_intent_detection():
    assert detect_intent("search files for python reports") == Intent.FILE_ACTION
    assert detect_intent("read file notes.txt") == Intent.FILE_ACTION
    assert detect_intent("organize my downloads directory") == Intent.FILE_ACTION
    assert detect_intent("compress this folder into zip") == Intent.FILE_ACTION
    assert detect_intent("find duplicate files") == Intent.FILE_ACTION


@pytest.mark.asyncio
async def test_chat_routes_and_executes_safe_file_query():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir).resolve()
        sample_file = temp_path / "hello.py"
        sample_file.write_text("print('hello world')", encoding="utf-8")

        test_settings = Settings(
            enable_file_tools=True,
            approved_file_roots=str(temp_path),
        )

        registry = register_file_tools(ToolRegistry(), app_settings=test_settings)
        planner = Planner(registry)

        plan = planner.plan(f"search files {sample_file.name}")
        assert plan.steps[0].tool == "search_files"

        # Test full chat flow
        provider = MockAIProvider()
        response = await chat(
            request=ChatRequest(message=f"search files {sample_file.name}"),
            registry=registry,
            provider=provider,
        )

        assert response.state == "COMPLETED"
        assert len(response.tool_results) == 1
        assert response.tool_results[0]["success"] is True
        assert response.tool_results[0]["tool"] == "search_files"
        assert response.intent == Intent.FILE_ACTION.value
