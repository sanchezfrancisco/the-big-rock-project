from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from semantic_code_navigator.chunking import chunk_python_file
from semantic_code_navigator.config import Settings
from semantic_code_navigator.discovery import discover_python_files
from semantic_code_navigator.store import IndexStore


@dataclass(frozen=True)
class IndexSummary:
    repository: str
    files: int
    chunks: int


def index_repository(repo_path: Path, settings: Settings) -> IndexSummary:
    if not repo_path.exists() or not repo_path.is_dir():
        raise ValueError(f"Repository path does not exist or is not a directory: {repo_path}")

    source_files = discover_python_files(repo_path, settings)
    payload = []
    chunk_count = 0
    for source_file in source_files:
        chunks = chunk_python_file(source_file)
        chunk_count += len(chunks)
        payload.append((source_file.relative_path, source_file.sha256, chunks))

    store = IndexStore(settings)
    try:
        store.replace_repository(repo_path, payload)
    finally:
        store.close()

    return IndexSummary(repository=str(repo_path.resolve()), files=len(source_files), chunks=chunk_count)

