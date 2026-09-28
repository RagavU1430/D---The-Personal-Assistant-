from __future__ import annotations

import os
import platform
import sys
from abc import ABC, abstractmethod
from pathlib import Path


class StartupManager(ABC):
    @property
    @abstractmethod
    def enabled(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        raise NotImplementedError


class InMemoryStartupManager(StartupManager):
    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled


class WindowsStartupManager(StartupManager):
    """Uses the per-user Startup folder, a standard visible Windows mechanism."""

    filename = "D-personal-assistant-startup.cmd"

    def __init__(self, command: str | None = None) -> None:
        backend_dir = Path(__file__).resolve().parents[1]
        self.command = command or f'cd /d "{backend_dir}" && "{sys.executable}" -m uvicorn app.main:app'

    @property
    def startup_path(self) -> Path:
        app_data = os.environ.get("APPDATA", "")
        return Path(app_data) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / self.filename

    @property
    def enabled(self) -> bool:
        return platform.system() == "Windows" and self.startup_path.exists()

    def set_enabled(self, enabled: bool) -> None:
        if platform.system() != "Windows":
            return
        if enabled:
            if not self.command:
                raise ValueError("A configured startup command is required.")
            self.startup_path.parent.mkdir(parents=True, exist_ok=True)
            self.startup_path.write_text(f"@echo off\n{self.command}\n", encoding="utf-8")
        elif self.startup_path.exists():
            self.startup_path.unlink()


def create_startup_manager(enabled: bool) -> StartupManager:
    manager: StartupManager
    if platform.system() == "Windows":
        command = os.environ.get("D_STARTUP_COMMAND")
        manager = WindowsStartupManager(command)
    else:
        manager = InMemoryStartupManager(enabled)
    if isinstance(manager, InMemoryStartupManager):
        manager.set_enabled(enabled)
    return manager
