from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceFile:
    path: Path
    relative_path: str
    content: str
    sha256: str


@dataclass(frozen=True)
class CodeChunk:
    file_path: str
    start_line: int
    end_line: int
    content: str
    symbol: str | None = None


@dataclass(frozen=True)
class SearchResult:
    chunk_id: int
    file_path: str
    start_line: int
    end_line: int
    content: str
    score: float
    symbol: str | None = None
    vector_score: float = 0.0
    keyword_score: float = 0.0


@dataclass(frozen=True)
class AnswerCitation:
    file_path: str
    start_line: int
    end_line: int
    score: float
