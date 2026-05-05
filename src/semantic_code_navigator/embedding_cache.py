from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


class EmbeddingCache:
    def __init__(self, cache_path: Path) -> None:
        self.path = cache_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.hits = 0
        self.misses = 0
        self._migrate()

    def close(self) -> None:
        self.connection.close()

    def _migrate(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS embeddings_cache (
              cache_key TEXT PRIMARY KEY,
              backend TEXT NOT NULL,
              model TEXT NOT NULL,
              dimensions INTEGER NOT NULL,
              text_hash TEXT NOT NULL,
              embedding TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_embeddings_cache_lookup
            ON embeddings_cache(backend, model, dimensions, text_hash);
            """
        )
        self.connection.commit()

    def get(
        self, backend: str, model: str, dimensions: int, text: str
    ) -> list[float] | None:
        text_hash = _hash_text(text)
        key = _cache_key(backend, model, dimensions, text_hash)
        row = self.connection.execute(
            "SELECT embedding FROM embeddings_cache WHERE cache_key = ?",
            (key,),
        ).fetchone()
        if row is None:
            self.misses += 1
            return None
        self.hits += 1
        return [float(item) for item in json.loads(row["embedding"])]

    def put(
        self,
        backend: str,
        model: str,
        dimensions: int,
        text: str,
        embedding: list[float],
    ) -> None:
        text_hash = _hash_text(text)
        key = _cache_key(backend, model, dimensions, text_hash)
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO embeddings_cache(
                  cache_key, backend, model, dimensions, text_hash, embedding
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (key, backend, model, dimensions, text_hash, json.dumps(embedding)),
            )

    def entry_count(self) -> int:
        row = self.connection.execute("SELECT COUNT(*) AS count FROM embeddings_cache").fetchone()
        if row is None:
            return 0
        return int(row["count"])

    def prune(self, max_entries: int) -> int:
        if max_entries < 0:
            max_entries = 0
        total = self.entry_count()
        to_delete = max(0, total - max_entries)
        if to_delete == 0:
            return 0
        with self.connection:
            self.connection.execute(
                """
                DELETE FROM embeddings_cache
                WHERE cache_key IN (
                  SELECT cache_key
                  FROM embeddings_cache
                  ORDER BY created_at ASC
                  LIMIT ?
                )
                """,
                (to_delete,),
            )
        return to_delete


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _cache_key(backend: str, model: str, dimensions: int, text_hash: str) -> str:
    return f"{backend}:{model}:{dimensions}:{text_hash}"
