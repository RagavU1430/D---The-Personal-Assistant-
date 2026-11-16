from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.tools.executor import ToolExecutor
from app.tools.files import (
    ReadFileTool,
    SearchFilesTool,
    WriteFileTool,
)
from app.tools.filesystem import FileSystemService, PathNotAllowedError, PathProtectedError
from app.tools.registry import ToolRegistry


@pytest.fixture
def temp_roots():
    with tempfile.TemporaryDirectory() as approved_dir, tempfile.TemporaryDirectory() as protected_dir:
        approved = Path(approved_dir).resolve()
        protected = Path(protected_dir).resolve()
        yield approved, protected


@pytest.fixture
def fs_service(temp_roots):
    approved, protected = temp_roots
    return FileSystemService(
        approved_roots=[approved],
        protected_roots=[protected],
        max_file_size_mb=10,
        large_file_threshold_mb=1,
    )


def test_path_resolution_and_traversal(fs_service, temp_roots):
    approved, _ = temp_roots

    valid_file = approved / "sub" / "test.txt"
    valid_resolved = fs_service.resolve_approved(valid_file, mutating=False)
    assert valid_resolved == valid_file.resolve()

    # Outside approved root must raise
    outside = approved.parent / "outside.txt"
    with pytest.raises(PathNotAllowedError):
        fs_service.resolve_approved(outside, mutating=False)


def test_protected_root_blocks_mutation(fs_service, temp_roots):
    _, protected = temp_roots

    protected_file = protected / "secret.txt"
    with pytest.raises(PathProtectedError):
        fs_service.resolve_approved(protected_file, mutating=True)


def test_search_and_read_files(fs_service, temp_roots):
    approved, _ = temp_roots
    (approved / "doc.txt").write_text("Hello D Assistant", encoding="utf-8")
    (approved / "nested").mkdir()
    (approved / "nested" / "script.py").write_text("print('test')", encoding="utf-8")

    matches = fs_service.search_files(pattern="*.py", root=str(approved))
    assert len(matches) == 1
    assert "script.py" in matches[0]["path"]

    content_data = fs_service.read_file(path=str(approved / "doc.txt"))
    assert content_data["content"] == "Hello D Assistant"
    assert content_data["truncated"] is False


def test_write_and_overwrite_protection(fs_service, temp_roots):
    approved, _ = temp_roots
    target = approved / "out.txt"

    res = fs_service.write_file(path=str(target), content="v1", overwrite=False)
    assert res["created"] is True
    assert target.read_text(encoding="utf-8") == "v1"

    # Writing without overwrite must fail
    with pytest.raises(FileExistsError):
        fs_service.write_file(path=str(target), content="v2", overwrite=False)

    # With overwrite
    res2 = fs_service.write_file(path=str(target), content="v2", overwrite=True)
    assert res2["overwrite"] is True
    assert target.read_text(encoding="utf-8") == "v2"


def test_copy_move_rename_files(fs_service, temp_roots):
    approved, _ = temp_roots
    orig = approved / "orig.txt"
    orig.write_text("sample content", encoding="utf-8")

    # Copy
    copy_dst = approved / "copied.txt"
    fs_service.copy_file(source=str(orig), destination=str(copy_dst))
    assert copy_dst.exists()
    assert orig.exists()

    # Move
    moved_dst = approved / "moved.txt"
    fs_service.move_file(source=str(copy_dst), destination=str(moved_dst))
    assert moved_dst.exists()
    assert not copy_dst.exists()

    # Rename
    res_rename = fs_service.rename_file(path=str(moved_dst), new_name="renamed.txt")
    assert res_rename["renamed"] is True
    assert (approved / "renamed.txt").exists()
    assert not moved_dst.exists()


def test_compress_directory(fs_service, temp_roots):
    approved, _ = temp_roots
    src_dir = approved / "to_compress"
    src_dir.mkdir()
    (src_dir / "f1.txt").write_text("data 1", encoding="utf-8")
    (src_dir / "f2.txt").write_text("data 2", encoding="utf-8")

    archive = approved / "result.zip"
    res = fs_service.compress_directory(source=str(src_dir), destination=str(archive), format="zip")
    assert archive.exists()
    assert res["size"] > 0


def test_find_duplicates_and_organize(fs_service, temp_roots):
    approved, _ = temp_roots
    f1 = approved / "a.txt"
    f2 = approved / "b.txt"
    f1.write_text("duplicate payload", encoding="utf-8")
    f2.write_text("duplicate payload", encoding="utf-8")

    # Duplicate check with min_size_mb=0 to catch small test files
    dupes = fs_service.find_duplicates(root=str(approved), min_size_mb=0)
    assert len(dupes) == 1
    assert len(dupes[0]["files"]) == 2

    # Organize directory (dry run)
    plan_data = fs_service.organize_directory(root=str(approved), by="extension", dry_run=True)
    assert plan_data["executed"] is False
    assert len(plan_data["plan"]) >= 2


@pytest.mark.asyncio
async def test_tool_executor_confirmation_for_mutating_tools(fs_service, temp_roots):
    approved, _ = temp_roots
    registry = ToolRegistry(
        [
            SearchFilesTool(fs_service),
            ReadFileTool(fs_service),
            WriteFileTool(fs_service),
        ]
    )

    executor = ToolExecutor(registry)

    # SAFE tool executes automatically
    target = approved / "info.txt"
    target.write_text("read me", encoding="utf-8")
    read_res = await executor.execute("read_file", {"path": str(target)})
    assert read_res.success is True
    assert read_res.data["content"] == "read me"

    # CONFIRM tool returns confirmation required without executing
    write_res = await executor.execute("write_file", {"path": str(approved / "new.txt"), "content": "blocked"})
    assert write_res.success is False
    assert write_res.error_code == "CONFIRMATION_REQUIRED"
    assert not (approved / "new.txt").exists()
