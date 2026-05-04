from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from semantic_code_navigator.config import SCHEMA_VERSION, Settings
from semantic_code_navigator.embeddings import cosine_similarity, embed_text
from semantic_code_navigator.models import CodeChunk, SearchResult


class IndexStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.path = settings.index_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._migrate()

    def close(self) -> None:
        self.connection.close()

    def reset(self) -> None:
        self.connection.close()
        if self.path.exists():
            self.path.unlink()
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS repositories (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              path TEXT NOT NULL UNIQUE,
              indexed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS source_files (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              repository_id INTEGER NOT NULL,
              path TEXT NOT NULL,
              sha256 TEXT NOT NULL,
              UNIQUE(repository_id, path),
              FOREIGN KEY(repository_id) REFERENCES repositories(id)
            );
            CREATE TABLE IF NOT EXISTS code_chunks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              source_file_id INTEGER NOT NULL,
              start_line INTEGER NOT NULL,
              end_line INTEGER NOT NULL,
              symbol TEXT,
              content TEXT NOT NULL,
              embedding TEXT NOT NULL,
              FOREIGN KEY(source_file_id) REFERENCES source_files(id)
            );
            CREATE TABLE IF NOT EXISTS queries (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              question TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self.connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        self.connection.commit()

    def replace_repository(self, repo_path: Path, files: list[tuple[str, str, list[CodeChunk]]]) -> None:
        repo = str(repo_path.resolve())
        with self.connection:
            self.connection.execute("DELETE FROM repositories WHERE path = ?", (repo,))
            cursor = self.connection.execute("INSERT INTO repositories(path) VALUES(?)", (repo,))
            repository_id = int(cursor.lastrowid)
            for relative_path, sha256, chunks in files:
                file_cursor = self.connection.execute(
                    "INSERT INTO source_files(repository_id, path, sha256) VALUES(?, ?, ?)",
                    (repository_id, relative_path, sha256),
                )
                source_file_id = int(file_cursor.lastrowid)
                for chunk in chunks:
                    embedding = embed_text(chunk.content, self.settings.vector_dimensions)
                    self.connection.execute(
                        """
                        INSERT INTO code_chunks(
                          source_file_id, start_line, end_line, symbol, content, embedding
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            source_file_id,
                            chunk.start_line,
                            chunk.end_line,
                            chunk.symbol,
                            chunk.content,
                            json.dumps(embedding),
                        ),
                    )

    def search(self, question: str, top_k: int | None = None) -> list[SearchResult]:
        query_vector = embed_text(question, self.settings.vector_dimensions)
        rows = self.connection.execute(
            """
            SELECT code_chunks.id, source_files.path, code_chunks.start_line,
                   code_chunks.end_line, code_chunks.symbol, code_chunks.content,
                   code_chunks.embedding
            FROM code_chunks
            JOIN source_files ON source_files.id = code_chunks.source_file_id
            """
        ).fetchall()
        results: list[SearchResult] = []
        for row in rows:
            vector = json.loads(row["embedding"])
            score = cosine_similarity(query_vector, vector)
            results.append(
                SearchResult(
                    chunk_id=int(row["id"]),
                    file_path=str(row["path"]),
                    start_line=int(row["start_line"]),
                    end_line=int(row["end_line"]),
                    symbol=row["symbol"],
                    content=str(row["content"]),
                    score=score,
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        return results[: top_k or self.settings.default_top_k]

    def record_query(self, question: str) -> None:
        with self.connection:
            self.connection.execute("INSERT INTO queries(question) VALUES(?)", (question,))

    def status(self) -> dict[str, int | str]:
        schema = self.connection.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version'"
        ).fetchone()
        repo_count = self.connection.execute("SELECT COUNT(*) FROM repositories").fetchone()[0]
        file_count = self.connection.execute("SELECT COUNT(*) FROM source_files").fetchone()[0]
        chunk_count = self.connection.execute("SELECT COUNT(*) FROM code_chunks").fetchone()[0]
        return {
            "schema_version": schema["value"] if schema else "unknown",
            "repositories": int(repo_count),
            "files": int(file_count),
            "chunks": int(chunk_count),
            "index_path": str(self.path),
        }

