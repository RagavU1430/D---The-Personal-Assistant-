from __future__ import annotations

import ctypes
import platform
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from ..config import Settings, settings
from ..security import RiskLevel
from .base import BaseTool, ToolResult
from .registry import ToolRegistry


class RecycleBinInput(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


def _approved_path(path: str, roots: list[Path]) -> Path | None:
    requested = Path(path).expanduser().resolve(strict=False)
    if any(requested == root or root in requested.parents for root in roots):
        return requested
    return None


class MoveToRecycleBinTool(BaseTool):
    name = "move_to_recycle_bin"
    description = "Move one approved file or folder to the Windows Recycle Bin."
    category = "files"
    risk_level = RiskLevel.CONFIRM
    input_schema = RecycleBinInput

    def __init__(self, approved_roots: list[Path]) -> None:
        self.approved_roots = approved_roots

    async def execute(self, arguments: RecycleBinInput | dict[str, Any]) -> ToolResult:
        parsed = self.input_schema.model_validate(arguments)
        target = _approved_path(parsed.path, self.approved_roots)
        if target is None:
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="PATH_NOT_ALLOWED",
                message="The path is outside the approved file roots.",
            )
        if not target.exists():
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="PATH_NOT_FOUND",
                message="The requested file or folder does not exist.",
            )
        if platform.system() != "Windows":
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="WINDOWS_ONLY",
                message="Recycle Bin integration is available only on Windows.",
            )
        try:
            path_buffer = ctypes.create_unicode_buffer(str(target) + "\0\0")
            operation = _SHFileOperation()
            operation.wFunc = _FO_DELETE
            operation.pFrom = ctypes.cast(path_buffer, ctypes.c_wchar_p)
            operation.fFlags = _FOF_ALLOWUNDO | _FOF_NOCONFIRMATION | _FOF_SILENT
            result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operation))
            if result != 0:
                return ToolResult(
                    success=False,
                    tool=self.name,
                    error_code="RECYCLE_BIN_ERROR",
                    message="Windows could not move the item to the Recycle Bin.",
                )
            return ToolResult(
                success=True,
                tool=self.name,
                data={"path": str(target), "permanent": False},
                message="Moved to the Recycle Bin.",
            )
        except Exception:
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="RECYCLE_BIN_ERROR",
                message="The Recycle Bin operation failed.",
            )


class _SHFileOperation(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("wFunc", ctypes.c_uint),
        ("pFrom", ctypes.c_wchar_p),
        ("pTo", ctypes.c_wchar_p),
        ("fFlags", ctypes.c_ushort),
        ("fAnyOperationsAborted", ctypes.c_bool),
        ("hNameMappings", ctypes.c_void_p),
        ("lpszProgressTitle", ctypes.c_wchar_p),
    ]


_FO_DELETE = 3
_FOF_SILENT = 0x0004
_FOF_NOCONFIRMATION = 0x0010
_FOF_ALLOWUNDO = 0x0040


def register_file_tools(registry: ToolRegistry, app_settings: Settings = settings) -> ToolRegistry:
    if not app_settings.enable_file_tools:
        return registry
    roots = [
        Path(item.strip()).expanduser().resolve(strict=False)
        for item in app_settings.approved_file_roots.split(",")
        if item.strip()
    ]
    registry.register(MoveToRecycleBinTool(roots))
    return registry
