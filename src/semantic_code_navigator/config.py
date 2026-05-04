from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Settings:
    index_path: Path = Path(".scn/index.sqlite3")
    max_file_bytes: int = 512_000
    vector_dimensions: int = 256
    default_top_k: int = 5

