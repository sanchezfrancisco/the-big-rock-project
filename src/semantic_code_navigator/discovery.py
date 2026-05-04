from __future__ import annotations

import hashlib
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
    files: list[SourceFile] = []
    for path in sorted(repo_path.rglob("*.py")):
        if should_ignore(path.relative_to(repo_path)):
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
                relative_path=path.relative_to(repo_path).as_posix(),
                content=content,
                sha256=digest,
            )
        )
    return files

