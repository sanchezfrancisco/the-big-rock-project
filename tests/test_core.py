from __future__ import annotations

from pathlib import Path

from semantic_code_navigator.chunking import chunk_python_file
from semantic_code_navigator.config import Settings
from semantic_code_navigator.discovery import discover_python_files, should_ignore
from semantic_code_navigator.indexer import index_repository
from semantic_code_navigator.models import SourceFile
from semantic_code_navigator.store import IndexStore


def test_should_ignore_common_generated_directories() -> None:
    assert should_ignore(Path(".git/config"))
    assert should_ignore(Path(".venv/Lib/site-packages/example.py"))
    assert not should_ignore(Path("src/app.py"))


def test_chunk_python_file_preserves_symbol_line_ranges() -> None:
    source = SourceFile(
        path=Path("sample.py"),
        relative_path="sample.py",
        sha256="abc",
        content="import os\n\n\ndef target():\n    return os.getcwd()\n",
    )

    chunks = chunk_python_file(source)

    target = next(chunk for chunk in chunks if chunk.symbol == "target")
    assert target.start_line == 4
    assert target.end_line == 5
    assert "return os.getcwd()" in target.content


def test_discovery_redacts_secrets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("API_KEY = 'sk-abcdefghijklmnopqrstuvwxyz'\n", encoding="utf-8")

    files = discover_python_files(repo, Settings(index_path=tmp_path / "idx.sqlite3"))

    assert len(files) == 1
    assert "[REDACTED_SECRET]" in files[0].content


def test_index_search_and_reset(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "auth.py").write_text(
        "def authenticate_user(username: str, password: str) -> bool:\n"
        "    return username == 'admin' and bool(password)\n",
        encoding="utf-8",
    )
    settings = Settings(index_path=tmp_path / "index.sqlite3")

    summary = index_repository(repo, settings)

    assert summary.files == 1
    assert summary.chunks >= 1

    store = IndexStore(settings)
    try:
        results = store.search("Where is authentication handled?", top_k=3)
        assert results
        assert results[0].file_path == "auth.py"
        assert results[0].start_line == 1

        status = store.status()
        assert status["files"] == 1
        assert status["chunks"] >= 1

        store.reset()
        assert store.status()["chunks"] == 0
    finally:
        store.close()

