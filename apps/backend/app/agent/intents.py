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

    # Phase 5 — Terminal / Developer JARVIS intent keywords (before SYSTEM_QUERY to avoid "status" conflict)
    terminal_keywords = (
        "git status", "git diff", "git log", "git branch", "git commit", "git push",
        "run tests", "run pytest", "run my tests", "what branch", "recent commits",
        "commit history", "analyze log", "analyze error", "analyze this error",
        "execute command", "test results", "show diff", "what changed",
        "current branch", "stage and commit",
    )
    if any(k in text for k in terminal_keywords):
        return Intent.TERMINAL_ACTION

    if any(keyword in text for keyword in ("system", "status", "cpu", "ram", "disk", "health")):
        return Intent.SYSTEM_QUERY

    if any(keyword in text for keyword in ("project", "debug", "error", "fix", "build", "run", "prepare")):
        return Intent.DEVELOPMENT_TASK

    file_keywords = (
        "file", "folder", "document", "locate", "directory", "compress", "zip", "duplicate", "organize"
    )
    if any(keyword in text for keyword in file_keywords):
        return Intent.FILE_ACTION
    if any(keyword in text for keyword in ("search file", "find all", "find files")):
        return Intent.FILE_ACTION
    if any(keyword in text for keyword in ("browser", "web", "website", "search")):
        return Intent.BROWSER_ACTION
    if any(keyword in text for keyword in ("terminal", "shell", "command", "powershell")):
        return Intent.TERMINAL_ACTION
    if "?" in message:
        return Intent.QUESTION
    return Intent.GENERAL_CHAT
