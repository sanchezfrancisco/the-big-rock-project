from __future__ import annotations

import json
import os
from pathlib import Path

from semantic_code_navigator.cli import main as cli_main
from semantic_code_navigator.chunking import chunk_python_file
from semantic_code_navigator.config import Settings
from semantic_code_navigator.discovery import discover_python_files, should_ignore
from semantic_code_navigator.indexer import index_repository
from semantic_code_navigator.models import SourceFile
from semantic_code_navigator.store import IndexStore
from semantic_code_navigator.eval import run_eval


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


def test_discovery_respects_scnignore(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".scnignore").write_text("ignored.py\nprivate/*\n", encoding="utf-8")
    (repo / "ignored.py").write_text("x = 1\n", encoding="utf-8")
    private = repo / "private"
    private.mkdir()
    (private / "secret.py").write_text("y = 2\n", encoding="utf-8")
    (repo / "kept.py").write_text("z = 3\n", encoding="utf-8")
    files = discover_python_files(repo, Settings(index_path=tmp_path / "idx.sqlite3"))
    names = {item.relative_path for item in files}
    assert "kept.py" in names
    assert "ignored.py" not in names
    assert "private/secret.py" not in names


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

        first_hits = store.status()["embedding_cache_hits"]
        store.search("Where is authentication handled?", top_k=3)
        second_hits = store.status()["embedding_cache_hits"]
        assert isinstance(first_hits, int)
        assert isinstance(second_hits, int)
        assert second_hits >= first_hits

        status = store.status()
        assert status["files"] == 1
        assert status["chunks"] >= 1

        store.reset()
        assert store.status()["chunks"] == 0
    finally:
        store.close()


def test_settings_from_env(tmp_path: Path) -> None:
    os.environ["SCN_EMBEDDING_BACKEND"] = "local"
    os.environ["SCN_HYBRID_KEYWORD_WEIGHT"] = "0.5"
    settings = Settings.from_env(index_path=tmp_path / "env.sqlite3")
    assert settings.embedding_backend == "local"
    assert settings.hybrid_keyword_weight == 0.5


def test_hybrid_retrieval_prefers_keyword_overlap(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "auth.py").write_text(
        "def authenticate_user(username: str, password: str) -> bool:\n"
        "    return username == 'admin' and bool(password)\n",
        encoding="utf-8",
    )
    (repo / "maths.py").write_text(
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n",
        encoding="utf-8",
    )
    settings = Settings(index_path=tmp_path / "hybrid.sqlite3", hybrid_keyword_weight=0.5)
    index_repository(repo, settings)
    store = IndexStore(settings)
    try:
        results = store.search("authenticate password", top_k=1)
        assert results
        assert results[0].file_path == "auth.py"
    finally:
        store.close()


def test_cli_json_status_and_doctor(tmp_path: Path, capsys: object) -> None:
    index_path = tmp_path / "cli.sqlite3"
    exit_code = cli_main(["--index-path", str(index_path), "--json", "status"])
    assert exit_code == 0
    out = capsys.readouterr().out.strip()  # type: ignore[attr-defined]
    payload = json.loads(out)
    assert payload["schema_version"] == "1"

    exit_code = cli_main(["--index-path", str(index_path), "--json", "doctor"])
    assert exit_code == 0
    out = capsys.readouterr().out.strip()  # type: ignore[attr-defined]
    doctor = json.loads(out)
    assert doctor["sqlite_ok"] is True


def test_cli_explain_json(tmp_path: Path, capsys: object) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "auth.py").write_text(
        "def authenticate_user(username: str, password: str) -> bool:\n"
        "    return username == 'admin' and bool(password)\n",
        encoding="utf-8",
    )
    index_path = tmp_path / "explain.sqlite3"
    assert cli_main(["--index-path", str(index_path), "index", str(repo)]) == 0
    exit_code = cli_main(
        [
            "--index-path",
            str(index_path),
            "--json",
            "explain",
            "authenticate password",
            "--top-k",
            "1",
        ]
    )
    assert exit_code == 0
    out = capsys.readouterr().out.strip()  # type: ignore[attr-defined]
    payload = json.loads(out.splitlines()[-1])
    assert payload["results"]
    first = payload["results"][0]
    assert "vector_score" in first
    assert "keyword_score" in first


def test_eval_report(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "auth.py").write_text("def authenticate_user():\n    return True\n", encoding="utf-8")
    settings = Settings(index_path=tmp_path / "eval.sqlite3")
    index_repository(repo, settings)
    dataset = tmp_path / "dataset.json"
    dataset.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "question": "authenticate user",
                        "expected_files": ["auth.py"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    report = run_eval(dataset, settings, top_k=3)
    assert report["summary"]["count"] == 1
