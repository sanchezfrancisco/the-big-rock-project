from __future__ import annotations

import hashlib
import fnmatch
from pathlib import Path

from semantic_code_navigator.config import Settings
from semantic_code_navigator.models import SourceFile
from semantic_code_navigator.security import redact_secrets


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
}


def should_ignore(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & IGNORED_DIRS)


def discover_python_files(repo_path: Path, settings: Settings) -> list[SourceFile]:
    repo_path = repo_path.resolve()
    ignore_patterns = _load_scnignore_patterns(repo_path)
    files: list[SourceFile] = []
    for path in sorted(repo_path.rglob("*.py")):
        relative = path.relative_to(repo_path)
        if should_ignore(relative) or _matches_scnignore(relative, ignore_patterns):
            continue
        if path.stat().st_size > settings.max_file_bytes:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scan = redact_secrets(raw)
        content = scan.redacted_text
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        files.append(
            SourceFile(
                path=path,
                relative_path=relative.as_posix(),
                content=content,
                sha256=digest,
            )
        )
    return files


def _load_scnignore_patterns(repo_path: Path) -> list[str]:
    ignore_file = repo_path / ".scnignore"
    if not ignore_file.exists():
        return []
    patterns: list[str] = []
    for line in ignore_file.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        patterns.append(value)
    return patterns


def _matches_scnignore(relative: Path, patterns: list[str]) -> bool:
    path_text = relative.as_posix()
    for pattern in patterns:
        normalized = pattern.lstrip("./")
        if fnmatch.fnmatch(path_text, normalized):
            return True
        if fnmatch.fnmatch(path_text, f"{normalized}/*"):
            return True
    return False
