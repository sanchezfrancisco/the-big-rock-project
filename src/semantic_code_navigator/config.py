from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Settings:
    index_path: Path = Path(".scn/index.sqlite3")
    embedding_cache_path: Path = Path(".scn/embeddings_cache.sqlite3")
    max_file_bytes: int = 512_000
    vector_dimensions: int = 256
    default_top_k: int = 5
    embedding_backend: str = "local"
    hybrid_keyword_weight: float = 0.35

    @staticmethod
    def from_env(index_path: Path | None = None) -> "Settings":
        backend = os.getenv("SCN_EMBEDDING_BACKEND", "local").strip().lower() or "local"
        hybrid = float(os.getenv("SCN_HYBRID_KEYWORD_WEIGHT", "0.35"))
        return Settings(
            index_path=index_path or Path(os.getenv("SCN_INDEX_PATH", ".scn/index.sqlite3")),
            embedding_cache_path=Path(
                os.getenv("SCN_EMBEDDING_CACHE_PATH", ".scn/embeddings_cache.sqlite3")
            ),
            max_file_bytes=int(os.getenv("SCN_MAX_FILE_BYTES", "512000")),
            vector_dimensions=int(os.getenv("SCN_VECTOR_DIMENSIONS", "256")),
            default_top_k=int(os.getenv("SCN_DEFAULT_TOP_K", "5")),
            embedding_backend=backend,
            hybrid_keyword_weight=max(0.0, min(1.0, hybrid)),
        )
