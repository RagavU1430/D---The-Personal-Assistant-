from __future__ import annotations

import fnmatch
import hashlib
import os
import re
import shutil
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal


class PathNotAllowedError(ValueError):
    """Raised when a path is outside the approved file roots."""


class PathProtectedError(ValueError):
    """Raised when an operation targets a protected root."""


class FileSystemService:
    def __init__(
        self,
        approved_roots: list[Path] | None = None,
        protected_roots: list[Path] | None = None,
        max_file_size_mb: int = 100,
        large_file_threshold_mb: int = 50,
    ) -> None:
        self.approved_roots = [
            root.expanduser().resolve(strict=False)
            for root in (approved_roots or [])
        ]
        self.protected_roots = [
            root.expanduser().resolve(strict=False)
            for root in (protected_roots or [])
        ]
        self.max_file_size_mb = max_file_size_mb
        self.large_file_threshold_mb = large_file_threshold_mb

    def is_under_root(self, target: Path, root: Path) -> bool:
        return target == root or root in target.parents

    def resolve_approved(self, path: str | Path, mutating: bool = False) -> Path:
        raw_path = Path(path).expanduser()
        if not raw_path.is_absolute():
            resolved = (Path.cwd() / raw_path).resolve(strict=False)
        else:
            resolved = raw_path.resolve(strict=False)

        if mutating and any(self.is_under_root(resolved, root) for root in self.protected_roots):
            raise PathProtectedError(f"The path '{path}' is within a protected directory and cannot be modified.")

        if not any(self.is_under_root(resolved, root) for root in self.approved_roots):
            raise PathNotAllowedError(f"The path '{path}' is outside the approved file roots.")

        return resolved

    def search_files(
        self,
        pattern: str,
        root: str | None = None,
        recursive: bool = True,
        max_results: int = 100,
    ) -> list[dict[str, Any]]:
        search_roots = (
            [self.resolve_approved(root, mutating=False)]
            if root
            else self.approved_roots
        )

        matches: list[dict[str, Any]] = []
        is_regex = any(c in pattern for c in r"^$[]()+{}|")
        regex = None
        if is_regex:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                regex = None

        for base_root in search_roots:
            if not base_root.exists():
                continue

            iterator = base_root.rglob("*") if recursive else base_root.glob("*")
            for item in iterator:
                if len(matches) >= max_results:
                    break
                if not item.is_file():
                    continue

                matched = False
                if regex is not None and (regex.search(item.name) or regex.search(str(item))):
                    matched = True
                elif (
                    fnmatch.fnmatch(item.name.lower(), pattern.lower())
                    or fnmatch.fnmatch(str(item).lower(), pattern.lower())
                ):
                    matched = True

                if matched:
                    stat = item.stat()
                    matches.append(
                        {
                            "path": str(item),
                            "name": item.name,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
                        }
                    )
            if len(matches) >= max_results:
                break

        return matches

    def read_file(
        self,
        path: str,
        max_bytes: int = 1_000_000,
        encoding: str = "utf-8",
    ) -> dict[str, Any]:
        target = self.resolve_approved(path, mutating=False)
        if not target.exists():
            raise FileNotFoundError(f"File not found: '{path}'")
        if not target.is_file():
            raise IsADirectoryError(f"Path is not a file: '{path}'")

        stat = target.stat()
        file_size = stat.st_size
        max_allowed_bytes = self.max_file_size_mb * 1024 * 1024
        if file_size > max_allowed_bytes:
            msg = f"File size ({file_size} bytes) exceeds limit ({max_allowed_bytes} bytes)."
            raise ValueError(msg)

        truncated = False
        with open(target, "rb") as f:
            raw_bytes = f.read(max_bytes + 1)
            if len(raw_bytes) > max_bytes:
                truncated = True
                raw_bytes = raw_bytes[:max_bytes]

        try:
            content = raw_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            raise ValueError(f"Could not decode file using '{encoding}' encoding: {exc}") from exc

        return {
            "path": str(target),
            "content": content,
            "size": file_size,
            "encoding": encoding,
            "truncated": truncated,
        }

    def write_file(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        overwrite: bool = False,
    ) -> dict[str, Any]:
        target = self.resolve_approved(path, mutating=True)
        existed = target.exists()
        if existed and not overwrite:
            raise FileExistsError(f"File '{path}' already exists and overwrite is set to False.")

        encoded_data = content.encode(encoding)
        max_allowed_bytes = self.max_file_size_mb * 1024 * 1024
        if len(encoded_data) > max_allowed_bytes:
            raise ValueError(f"Payload size exceeds maximum file limit ({max_allowed_bytes} bytes).")

        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(encoded_data)

        return {
            "path": str(target),
            "bytes_written": len(encoded_data),
            "created": not existed,
            "overwrite": overwrite,
        }

    def copy_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        src = self.resolve_approved(source, mutating=False)
        dst = self.resolve_approved(destination, mutating=True)

        if not src.exists():
            raise FileNotFoundError(f"Source file not found: '{source}'")

        if dst.is_dir():
            dst = dst / src.name

        if dst.exists() and not overwrite:
            raise FileExistsError(f"Destination '{dst}' already exists and overwrite is False.")

        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

        return {
            "source": str(src),
            "destination": str(dst),
            "copied": True,
        }

    def move_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        src = self.resolve_approved(source, mutating=True)
        dst = self.resolve_approved(destination, mutating=True)

        if not src.exists():
            raise FileNotFoundError(f"Source file not found: '{source}'")

        if dst.is_dir():
            dst = dst / src.name

        if dst.exists():
            if not overwrite:
                raise FileExistsError(f"Destination '{dst}' already exists and overwrite is False.")
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

        return {
            "source": str(src),
            "destination": str(dst),
            "moved": True,
        }

    def rename_file(self, path: str, new_name: str) -> dict[str, Any]:
        src = self.resolve_approved(path, mutating=True)
        if not src.exists():
            raise FileNotFoundError(f"Path not found: '{path}'")

        dst = src.parent / new_name
        self.resolve_approved(dst, mutating=True)

        if dst.exists():
            raise FileExistsError(f"Target '{dst.name}' already exists.")

        src.rename(dst)
        return {
            "old_path": str(src),
            "new_path": str(dst),
            "renamed": True,
        }

    def compress_directory(
        self,
        source: str,
        destination: str,
        format: Literal["zip", "tar.gz"] = "zip",
    ) -> dict[str, Any]:
        src = self.resolve_approved(source, mutating=False)
        dst = self.resolve_approved(destination, mutating=True)

        if not src.exists() or not src.is_dir():
            raise NotADirectoryError(f"Source is not a directory: '{source}'")

        dst.parent.mkdir(parents=True, exist_ok=True)

        if format == "zip":
            with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(src):
                    for file in files:
                        file_path = Path(root) / file
                        archive_name = file_path.relative_to(src)
                        zf.write(file_path, archive_name)
        elif format == "tar.gz":
            with tarfile.open(dst, "w:gz") as tf:
                tf.add(src, arcname=".")
        else:
            raise ValueError(f"Unsupported format '{format}'. Use 'zip' or 'tar.gz'.")

        return {
            "source": str(src),
            "destination": str(dst),
            "format": format,
            "size": dst.stat().st_size,
        }

    def list_large_files(
        self,
        root: str | None = None,
        threshold_mb: int = 50,
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        search_roots = (
            [self.resolve_approved(root, mutating=False)]
            if root
            else self.approved_roots
        )
        min_bytes = threshold_mb * 1024 * 1024
        large_files: list[dict[str, Any]] = []

        for base_root in search_roots:
            if not base_root.exists():
                continue
            for item in base_root.rglob("*"):
                if item.is_file():
                    try:
                        sz = item.stat().st_size
                        if sz >= min_bytes:
                            large_files.append(
                                {
                                    "path": str(item),
                                    "name": item.name,
                                    "size_bytes": sz,
                                    "size_mb": round(sz / (1024 * 1024), 2),
                                }
                            )
                    except OSError:
                        continue

        large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
        return large_files[:max_results]

    def find_duplicates(
        self,
        root: str | None = None,
        min_size_mb: int = 1,
        max_groups: int = 20,
    ) -> list[dict[str, Any]]:
        search_roots = (
            [self.resolve_approved(root, mutating=False)]
            if root
            else self.approved_roots
        )
        min_bytes = min_size_mb * 1024 * 1024
        by_size: dict[int, list[Path]] = {}

        for base_root in search_roots:
            if not base_root.exists():
                continue
            for item in base_root.rglob("*"):
                if item.is_file():
                    try:
                        sz = item.stat().st_size
                        if sz >= min_bytes:
                            by_size.setdefault(sz, []).append(item)
                    except OSError:
                        continue

        groups: list[dict[str, Any]] = []
        for sz, files in by_size.items():
            if len(files) < 2:
                continue
            by_hash: dict[str, list[str]] = {}
            for f in files:
                try:
                    h = hashlib.sha256()
                    with open(f, "rb") as stream:
                        while chunk := stream.read(65536):
                            h.update(chunk)
                    digest = h.hexdigest()
                    by_hash.setdefault(digest, []).append(str(f))
                except OSError:
                    continue

            for digest, match_list in by_hash.items():
                if len(match_list) > 1:
                    groups.append(
                        {
                            "hash": digest,
                            "size_bytes": sz,
                            "size_mb": round(sz / (1024 * 1024), 2),
                            "count": len(match_list),
                            "files": match_list,
                        }
                    )
                if len(groups) >= max_groups:
                    break
            if len(groups) >= max_groups:
                break

        return groups

    def organize_directory(
        self,
        root: str,
        by: Literal["extension", "date", "size"] = "extension",
        dry_run: bool = True,
    ) -> dict[str, Any]:
        target_dir = self.resolve_approved(root, mutating=not dry_run)
        if not target_dir.exists() or not target_dir.is_dir():
            raise NotADirectoryError(f"Directory not found: '{root}'")

        plan: list[dict[str, str]] = []
        for item in target_dir.iterdir():
            if not item.is_file():
                continue

            subfolder = "other"
            if by == "extension":
                ext = item.suffix.lstrip(".").lower()
                subfolder = ext if ext else "no_extension"
            elif by == "date":
                stat = item.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC)
                subfolder = mtime.strftime("%Y-%m")
            elif by == "size":
                sz = item.stat().st_size
                if sz < 1024 * 1024:
                    subfolder = "small_<1MB"
                elif sz < 50 * 1024 * 1024:
                    subfolder = "medium_1-50MB"
                else:
                    subfolder = "large_>50MB"

            dest_folder = target_dir / subfolder
            dest_path = dest_folder / item.name
            if dest_path != item:
                plan.append({"source": str(item), "destination": str(dest_path)})

        if not dry_run:
            for op in plan:
                s = Path(op["source"])
                d = Path(op["destination"])
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(s), str(d))

        return {
            "root": str(target_dir),
            "by": by,
            "dry_run": dry_run,
            "items_count": len(plan),
            "plan": plan,
            "executed": not dry_run,
        }
