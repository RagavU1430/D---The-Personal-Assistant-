from __future__ import annotations

from enum import StrEnum


class Intent(StrEnum):
    GENERAL_CHAT = "GENERAL_CHAT"
    QUESTION = "QUESTION"
    SYSTEM_QUERY = "SYSTEM_QUERY"
    APPLICATION_ACTION = "APPLICATION_ACTION"
    FILE_ACTION = "FILE_ACTION"
    TERMINAL_ACTION = "TERMINAL_ACTION"
    BROWSER_ACTION = "BROWSER_ACTION"
    DEVELOPMENT_TASK = "DEVELOPMENT_TASK"
    MULTI_STEP_TASK = "MULTI_STEP_TASK"
    UNKNOWN = "UNKNOWN"


def detect_intent(message: str) -> Intent:
    text = message.lower()
    if any(keyword in text for keyword in ("open", "launch", "start", "vscode", "code")):
        return Intent.APPLICATION_ACTION
    if any(keyword in text for keyword in ("system", "status", "cpu", "ram", "disk", "health")):
        return Intent.SYSTEM_QUERY
    if any(keyword in text for keyword in ("project", "debug", "error", "fix", "build", "run", "prepare")):
        return Intent.DEVELOPMENT_TASK
    if any(keyword in text for keyword in ("browser", "web", "website", "search")):
        return Intent.BROWSER_ACTION
    if any(keyword in text for keyword in ("file", "folder", "document", "locate")):
        return Intent.FILE_ACTION
    if any(keyword in text for keyword in ("terminal", "shell", "command", "power shell", "powershell")):
        return Intent.TERMINAL_ACTION
    if "?" in message:
        return Intent.QUESTION
    return Intent.GENERAL_CHAT
