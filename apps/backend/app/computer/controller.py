from __future__ import annotations

import asyncio
import os
import platform
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ComputerController(ABC):
    def __init__(self) -> None:
        self._enabled = True
        self._cancel_event = asyncio.Event()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def emergency_stop(self) -> None:
        self._enabled = False
        self._cancel_event.set()

    def resume(self) -> None:
        self._cancel_event = asyncio.Event()
        self._enabled = True

    def check_available(self) -> None:
        if not self._enabled:
            raise ComputerControlDisabledError("Computer control is disabled.")
        if self._cancel_event.is_set():
            raise ComputerActionCancelledError("Computer action was cancelled.")

    @abstractmethod
    async def open_application(self, application: str, executable: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def close_application(self, title: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def focus_window(self, title: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def minimize_window(self, title: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def maximize_window(self, title: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def move_mouse(self, x: int, y: int) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def click(self, x: int, y: int, double: bool = False) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def type_text(self, text: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def press_key(self, key: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def hotkey(self, keys: list[str]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def screenshot(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_active_window(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def list_windows(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class ComputerControlDisabledError(RuntimeError):
    pass


class ComputerActionCancelledError(RuntimeError):
    pass


class FakeComputerController(ComputerController):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def _call(self, name: str, data: dict[str, Any]) -> dict[str, Any]:
        self.check_available()
        self.calls.append((name, data))
        return {"action": name, **data}

    async def open_application(self, application: str, executable: str) -> dict[str, Any]:
        return self._call("open_application", {"application": application})

    async def close_application(self, title: str) -> dict[str, Any]:
        return self._call("close_application", {"title": title})

    async def focus_window(self, title: str) -> dict[str, Any]:
        return self._call("focus_window", {"title": title})

    async def minimize_window(self, title: str) -> dict[str, Any]:
        return self._call("minimize_window", {"title": title})

    async def maximize_window(self, title: str) -> dict[str, Any]:
        return self._call("maximize_window", {"title": title})

    async def move_mouse(self, x: int, y: int) -> dict[str, Any]:
        return self._call("move_mouse", {"x": x, "y": y})

    async def click(self, x: int, y: int, double: bool = False) -> dict[str, Any]:
        return self._call("double_click" if double else "click", {"x": x, "y": y})

    async def type_text(self, text: str) -> dict[str, Any]:
        return self._call("type_text", {"characters": len(text)})

    async def press_key(self, key: str) -> dict[str, Any]:
        return self._call("press_key", {"key": key})

    async def hotkey(self, keys: list[str]) -> dict[str, Any]:
        return self._call("hotkey", {"keys": keys})

    async def screenshot(self) -> dict[str, Any]:
        return self._call("take_screenshot", {"temporary": True})

    async def get_active_window(self) -> dict[str, Any]:
        return self._call("get_active_window", {"title": "Fake Window", "state": "active"})

    async def list_windows(self) -> list[dict[str, Any]]:
        self.check_available()
        self.calls.append(("list_windows", {}))
        return [{"title": "Fake Window", "process": "fake", "state": "active"}]


class WindowsComputerController(ComputerController):
    def _require_windows(self) -> None:
        self.check_available()
        if platform.system() != "Windows":
            raise RuntimeError("Windows computer control is available only on Windows.")

    async def open_application(self, application: str, executable: str) -> dict[str, Any]:
        self._require_windows()
        await asyncio.to_thread(subprocess.Popen, [executable], shell=False)
        return {"application": application, "started": True}

    async def close_application(self, title: str) -> dict[str, Any]:
        self._require_windows()
        window = await self._find_window(title)
        if not window:
            raise RuntimeError("Window not found.")
        import ctypes

        ctypes.windll.user32.PostMessageW(window, 0x0010, 0, 0)
        return {"title": title, "closed": True}

    async def focus_window(self, title: str) -> dict[str, Any]:
        self._require_windows()
        window = await self._find_window(title)
        if not window:
            raise RuntimeError("Window not found.")
        import ctypes

        ctypes.windll.user32.SetForegroundWindow(window)
        return {"title": title, "focused": True}

    async def minimize_window(self, title: str) -> dict[str, Any]:
        return await self._show_window(title, 6)

    async def maximize_window(self, title: str) -> dict[str, Any]:
        return await self._show_window(title, 3)

    async def _show_window(self, title: str, command: int) -> dict[str, Any]:
        self._require_windows()
        window = await self._find_window(title)
        if not window:
            raise RuntimeError("Window not found.")
        import ctypes

        ctypes.windll.user32.ShowWindow(window, command)
        return {"title": title, "updated": True}

    async def move_mouse(self, x: int, y: int) -> dict[str, Any]:
        self._require_windows()
        pyautogui = self._pyautogui()
        await asyncio.to_thread(pyautogui.moveTo, x, y)
        return {"x": x, "y": y}

    async def click(self, x: int, y: int, double: bool = False) -> dict[str, Any]:
        self._require_windows()
        pyautogui = self._pyautogui()
        await asyncio.to_thread(pyautogui.click, x, y, clicks=2 if double else 1, interval=0.1)
        return {"x": x, "y": y, "double": double}

    async def type_text(self, text: str) -> dict[str, Any]:
        self._require_windows()
        pyautogui = self._pyautogui()
        await asyncio.to_thread(pyautogui.write, text, interval=0.01)
        return {"characters": len(text)}

    async def press_key(self, key: str) -> dict[str, Any]:
        self._require_windows()
        pyautogui = self._pyautogui()
        await asyncio.to_thread(pyautogui.press, key.lower())
        return {"key": key}

    async def hotkey(self, keys: list[str]) -> dict[str, Any]:
        self._require_windows()
        pyautogui = self._pyautogui()
        await asyncio.to_thread(pyautogui.hotkey, *(key.lower() for key in keys))
        return {"keys": keys}

    async def screenshot(self) -> dict[str, Any]:
        self._require_windows()
        pyautogui = self._pyautogui()
        path = Path(os.environ.get("TEMP", ".")) / "d-assistant-screenshot.png"
        await asyncio.to_thread(pyautogui.screenshot, str(path))
        return {"temporary_path": str(path), "temporary": True}

    async def get_active_window(self) -> dict[str, Any]:
        self._require_windows()
        import ctypes

        handle = ctypes.windll.user32.GetForegroundWindow()
        title = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.GetWindowTextW(handle, title, 512)
        return {"title": title.value, "process": "unknown", "state": "active"}

    async def list_windows(self) -> list[dict[str, Any]]:
        self._require_windows()
        import ctypes

        windows: list[dict[str, Any]] = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def callback(handle: int, _: int) -> bool:
            if ctypes.windll.user32.IsWindowVisible(handle):
                title = ctypes.create_unicode_buffer(512)
                ctypes.windll.user32.GetWindowTextW(handle, title, 512)
                if title.value:
                    windows.append({"title": title.value, "process": "unknown", "state": "visible"})
            return True

        ctypes.windll.user32.EnumWindows(callback_type(callback), 0)
        return windows

    async def _find_window(self, title: str) -> int | None:
        import ctypes

        return ctypes.windll.user32.FindWindowW(None, title) or None

    @staticmethod
    def _pyautogui() -> Any:
        try:
            import pyautogui
        except ImportError as exc:
            raise RuntimeError("PyAutoGUI is required for mouse and keyboard control.") from exc
        return pyautogui
