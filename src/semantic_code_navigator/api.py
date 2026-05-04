from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from semantic_code_navigator.config import Settings
from semantic_code_navigator.indexer import index_repository
from semantic_code_navigator.qa import build_answer
from semantic_code_navigator.store import IndexStore


app = FastAPI(title="Semantic Code Navigator", version="0.1.0")


class IndexRequest(BaseModel):
    repo_path: str
    index_path: str = ".scn/index.sqlite3"


class AskRequest(BaseModel):
    question: str
    index_path: str = ".scn/index.sqlite3"
    top_k: int = 5


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/index")
def index_repo(request: IndexRequest) -> dict[str, int | str]:
    summary = index_repository(Path(request.repo_path), Settings(index_path=Path(request.index_path)))
    return {"repository": summary.repository, "files": summary.files, "chunks": summary.chunks}


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, object]:
    store = IndexStore(Settings(index_path=Path(request.index_path)))
    try:
        results = store.search(request.question, top_k=request.top_k)
        store.record_query(request.question)
    finally:
        store.close()
    answer = build_answer(request.question, results)
    return {
        "question": answer.question,
        "summary": answer.summary,
        "citations": [citation.__dict__ for citation in answer.citations],
    }


@app.get("/status")
def status(index_path: str = ".scn/index.sqlite3") -> dict[str, int | str]:
    store = IndexStore(Settings(index_path=Path(index_path)))
    try:
        return store.status()
    finally:
        store.close()

