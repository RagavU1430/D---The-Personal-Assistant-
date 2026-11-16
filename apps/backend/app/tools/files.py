from __future__ import annotations

import ctypes
import platform
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..config import Settings, settings
from ..security import RiskLevel
from .base import BaseTool, ToolResult
from .filesystem import FileSystemService, PathNotAllowedError, PathProtectedError
from .registry import ToolRegistry


class RecycleBinInput(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


class SearchFilesInput(BaseModel):
    pattern: str = Field(min_length=1, max_length=256)
    root: str | None = None
    recursive: bool = True
    max_results: int = Field(default=100, ge=1, le=1000)


class ReadFileInput(BaseModel):
    path: str = Field(min_length=1, max_length=4096)
    max_bytes: int = Field(default=1_000_000, ge=1, le=10_000_000)
    encoding: str = "utf-8"


class WriteFileInput(BaseModel):
    path: str = Field(min_length=1, max_length=4096)
    content: str
    encoding: str = "utf-8"
    overwrite: bool = False


class CopyFileInput(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    destination: str = Field(min_length=1, max_length=4096)
    overwrite: bool = False


class MoveFileInput(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    destination: str = Field(min_length=1, max_length=4096)
    overwrite: bool = False


class RenameFileInput(BaseModel):
    path: str = Field(min_length=1, max_length=4096)
    new_name: str = Field(min_length=1, max_length=256, pattern=r"^[^<>:\"/\\|?*\x00-\x1F]+$")


class CompressDirectoryInput(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    destination: str = Field(min_length=1, max_length=4096)
    format: Literal["zip", "tar.gz"] = "zip"


class ListLargeFilesInput(BaseModel):
    root: str | None = None
    threshold_mb: int = Field(default=50, ge=1, le=10000)
    max_results: int = Field(default=50, ge=1, le=500)


class FindDuplicatesInput(BaseModel):
    root: str | None = None
    min_size_mb: int = Field(default=1, ge=0, le=1000)
    max_groups: int = Field(default=20, ge=1, le=100)


class OrganizeDirectoryInput(BaseModel):
    root: str = Field(min_length=1, max_length=4096)
    by: Literal["extension", "date", "size"] = "extension"
    dry_run: bool = True


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


class BaseFileTool(BaseTool):
    category = "files"

    def __init__(self, fs: FileSystemService) -> None:
        self.fs = fs


class SearchFilesTool(BaseFileTool):
    name = "search_files"
    description = "Search for files by name, pattern, or regex within approved directories."
    risk_level = RiskLevel.SAFE
    input_schema = SearchFilesInput

    async def execute(self, arguments: SearchFilesInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            matches = self.fs.search_files(
                pattern=parsed.pattern,
                root=parsed.root,
                recursive=parsed.recursive,
                max_results=parsed.max_results,
            )
            return ToolResult(
                success=True,
                tool=self.name,
                data={"matches": matches, "count": len(matches)},
                message=f"Found {len(matches)} matching files.",
            )
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class ReadFileTool(BaseFileTool):
    name = "read_file"
    description = "Read the contents of a text file within approved directories."
    risk_level = RiskLevel.SAFE
    input_schema = ReadFileInput

    async def execute(self, arguments: ReadFileInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.read_file(
                path=parsed.path,
                max_bytes=parsed.max_bytes,
                encoding=parsed.encoding,
            )
            return ToolResult(success=True, tool=self.name, data=res, message="File read successfully.")
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except FileNotFoundError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_FOUND", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class WriteFileTool(BaseFileTool):
    name = "write_file"
    description = "Create or write content to a file in an approved directory (CONFIRM required)."
    risk_level = RiskLevel.CONFIRM
    input_schema = WriteFileInput

    async def execute(self, arguments: WriteFileInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.write_file(
                path=parsed.path,
                content=parsed.content,
                encoding=parsed.encoding,
                overwrite=parsed.overwrite,
            )
            return ToolResult(success=True, tool=self.name, data=res, message="File written successfully.")
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except PathProtectedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_PROTECTED", message=str(exc))
        except FileExistsError as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ALREADY_EXISTS", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class CopyFileTool(BaseFileTool):
    name = "copy_file"
    description = "Copy a file or directory within approved directories (CONFIRM required)."
    risk_level = RiskLevel.CONFIRM
    input_schema = CopyFileInput

    async def execute(self, arguments: CopyFileInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.copy_file(
                source=parsed.source,
                destination=parsed.destination,
                overwrite=parsed.overwrite,
            )
            return ToolResult(success=True, tool=self.name, data=res, message="File copied successfully.")
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except PathProtectedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_PROTECTED", message=str(exc))
        except FileNotFoundError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_FOUND", message=str(exc))
        except FileExistsError as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ALREADY_EXISTS", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class MoveFileTool(BaseFileTool):
    name = "move_file"
    description = "Move a file or directory within approved directories (CONFIRM required)."
    risk_level = RiskLevel.CONFIRM
    input_schema = MoveFileInput

    async def execute(self, arguments: MoveFileInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.move_file(
                source=parsed.source,
                destination=parsed.destination,
                overwrite=parsed.overwrite,
            )
            return ToolResult(success=True, tool=self.name, data=res, message="File moved successfully.")
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except PathProtectedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_PROTECTED", message=str(exc))
        except FileNotFoundError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_FOUND", message=str(exc))
        except FileExistsError as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ALREADY_EXISTS", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class RenameFileTool(BaseFileTool):
    name = "rename_file"
    description = "Rename a file or directory within approved directories (CONFIRM required)."
    risk_level = RiskLevel.CONFIRM
    input_schema = RenameFileInput

    async def execute(self, arguments: RenameFileInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.rename_file(
                path=parsed.path,
                new_name=parsed.new_name,
            )
            return ToolResult(success=True, tool=self.name, data=res, message="File renamed successfully.")
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except PathProtectedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_PROTECTED", message=str(exc))
        except FileNotFoundError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_FOUND", message=str(exc))
        except FileExistsError as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ALREADY_EXISTS", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class CompressDirectoryTool(BaseFileTool):
    name = "compress_directory"
    description = "Compress a directory into a .zip or .tar.gz archive (CONFIRM required)."
    risk_level = RiskLevel.CONFIRM
    input_schema = CompressDirectoryInput

    async def execute(self, arguments: CompressDirectoryInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.compress_directory(
                source=parsed.source,
                destination=parsed.destination,
                format=parsed.format,
            )
            return ToolResult(success=True, tool=self.name, data=res, message="Directory compressed successfully.")
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except PathProtectedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_PROTECTED", message=str(exc))
        except (FileNotFoundError, NotADirectoryError) as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_FOUND", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class ListLargeFilesTool(BaseFileTool):
    name = "list_large_files"
    description = "List files exceeding a size threshold within approved directories."
    risk_level = RiskLevel.SAFE
    input_schema = ListLargeFilesInput

    async def execute(self, arguments: ListLargeFilesInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.list_large_files(
                root=parsed.root,
                threshold_mb=parsed.threshold_mb,
                max_results=parsed.max_results,
            )
            return ToolResult(
                success=True,
                tool=self.name,
                data={"files": res, "count": len(res)},
                message=f"Found {len(res)} large files.",
            )
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class FindDuplicatesTool(BaseFileTool):
    name = "find_duplicates"
    description = "Detect duplicate files by SHA-256 hash within approved directories."
    risk_level = RiskLevel.SAFE
    input_schema = FindDuplicatesInput

    async def execute(self, arguments: FindDuplicatesInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.find_duplicates(
                root=parsed.root,
                min_size_mb=parsed.min_size_mb,
                max_groups=parsed.max_groups,
            )
            return ToolResult(
                success=True,
                tool=self.name,
                data={"groups": res, "group_count": len(res)},
                message=f"Found {len(res)} duplicate groups.",
            )
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


class OrganizeDirectoryTool(BaseFileTool):
    name = "organize_directory"
    description = "Organize files in a directory by extension, date, or size (CONFIRM required for execution)."
    risk_level = RiskLevel.CONFIRM
    input_schema = OrganizeDirectoryInput

    async def execute(self, arguments: OrganizeDirectoryInput | dict[str, Any]) -> ToolResult:
        try:
            parsed = self.input_schema.model_validate(arguments)
            res = self.fs.organize_directory(
                root=parsed.root,
                by=parsed.by,
                dry_run=parsed.dry_run,
            )
            msg = "Organization plan generated (dry run)." if parsed.dry_run else "Directory organized successfully."
            return ToolResult(success=True, tool=self.name, data=res, message=msg)
        except PathNotAllowedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_ALLOWED", message=str(exc))
        except PathProtectedError as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_PROTECTED", message=str(exc))
        except (FileNotFoundError, NotADirectoryError) as exc:
            return ToolResult(success=False, tool=self.name, error_code="PATH_NOT_FOUND", message=str(exc))
        except Exception as exc:
            return ToolResult(success=False, tool=self.name, error_code="FILE_ACTION_ERROR", message=str(exc))


def register_file_tools(registry: ToolRegistry, app_settings: Settings = settings) -> ToolRegistry:
    if not app_settings.enable_file_tools:
        return registry

    approved_roots = [
        Path(item.strip()).expanduser().resolve(strict=False)
        for item in app_settings.approved_file_roots.split(",")
        if item.strip()
    ]
    protected_roots = [
        Path(item.strip()).expanduser().resolve(strict=False)
        for item in app_settings.protected_file_roots.split(",")
        if item.strip()
    ]

    fs = FileSystemService(
        approved_roots=approved_roots,
        protected_roots=protected_roots,
        max_file_size_mb=app_settings.max_file_size_mb,
        large_file_threshold_mb=app_settings.large_file_threshold_mb,
    )

    tools = (
        MoveToRecycleBinTool(approved_roots),
        SearchFilesTool(fs),
        ReadFileTool(fs),
        WriteFileTool(fs),
        CopyFileTool(fs),
        MoveFileTool(fs),
        RenameFileTool(fs),
        CompressDirectoryTool(fs),
        ListLargeFilesTool(fs),
        FindDuplicatesTool(fs),
        OrganizeDirectoryTool(fs),
    )
    for tool in tools:
        registry.register(tool)
    return registry
