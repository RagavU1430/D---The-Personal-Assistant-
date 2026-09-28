from __future__ import annotations

from enum import StrEnum

from .computer.controller import ComputerController
from .config import Settings, settings
from .startup import StartupManager, create_startup_manager
from .tools.computer import register_computer_tools
from .tools.registry import ToolRegistry
from .tools.system import register_system_tools


class RuntimeState(StrEnum):
    STARTING = "STARTING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class DApplicationLifecycle:
    def __init__(
        self,
        startup_manager: StartupManager | None = None,
        controller: ComputerController | None = None,
        app_settings: Settings | None = None,
    ) -> None:
        self.settings = app_settings or settings
        self.startup_manager = startup_manager or create_startup_manager(self.settings.start_with_windows)
        self.controller = controller
        self.registry: ToolRegistry | None = None
        self.state = RuntimeState.STOPPED

    async def startup(self) -> None:
        self.state = RuntimeState.STARTING
        try:
            if self.controller is not None:
                self.controller.resume()
                self.registry = register_computer_tools(ToolRegistry(), self.controller)
            else:
                self.registry = register_system_tools(ToolRegistry())
            self.state = RuntimeState.READY
        except Exception:
            self.state = RuntimeState.DEGRADED
            raise

    async def shutdown(self) -> None:
        self.state = RuntimeState.STOPPING
        if self.controller is not None:
            self.controller.emergency_stop()
        self.state = RuntimeState.STOPPED

    async def set_start_with_windows(self, enabled: bool) -> None:
        self.startup_manager.set_enabled(enabled)

    def emergency_stop(self) -> None:
        if self.controller is not None:
            self.controller.emergency_stop()

    def resume_computer_control(self) -> None:
        if self.controller is not None:
            self.controller.resume()

    def health(self) -> dict[str, object]:
        return {
            "assistant": "D",
            "status": self.state.value,
            "computer_control": bool(self.controller and self.controller.enabled),
            "tool_system": self.registry is not None,
            "ai_provider": bool(self.settings.ai_provider or "mock"),
            "startup_enabled": self.startup_manager.enabled,
            "background_mode": self.settings.background_mode,
        }
