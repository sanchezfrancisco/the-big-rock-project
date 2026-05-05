from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from semantic_code_navigator.config import Settings
from semantic_code_navigator.indexer import index_repository
from semantic_code_navigator.qa import build_answer
from semantic_code_navigator.store import IndexStore


app = FastAPI(title="Semantic Code Navigator", version="0.1.0")
STATIC_DIR = Path(__file__).resolve().parent / "web"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class IndexRequest(BaseModel):
    repo_path: str
    index_path: str = ".scn/index.sqlite3"


class AskRequest(BaseModel):
    question: str
    index_path: str = ".scn/index.sqlite3"
    top_k: int = 5


class ExplainRequest(BaseModel):
    question: str
    index_path: str = ".scn/index.sqlite3"
    top_k: int = 5


@app.get("/")
def ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/index")
def index_repo(request: IndexRequest) -> dict[str, int | str]:
    summary = index_repository(
        Path(request.repo_path),
        Settings.from_env(index_path=Path(request.index_path)),
    )
    return {"repository": summary.repository, "files": summary.files, "chunks": summary.chunks}


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, object]:
    store = IndexStore(Settings.from_env(index_path=Path(request.index_path)))
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
    store = IndexStore(Settings.from_env(index_path=Path(index_path)))
    try:
        return store.status()
    finally:
        store.close()


@app.post("/explain")
def explain(request: ExplainRequest) -> dict[str, object]:
    settings = Settings.from_env(index_path=Path(request.index_path))
    store = IndexStore(settings)
    try:
        results = store.search(request.question, top_k=request.top_k)
    finally:
        store.close()
    return {
        "question": request.question,
        "backend": settings.embedding_backend,
        "hybrid_keyword_weight": settings.hybrid_keyword_weight,
        "results": [
            {
                "file_path": result.file_path,
                "start_line": result.start_line,
                "end_line": result.end_line,
                "symbol": result.symbol,
                "score": result.score,
                "vector_score": result.vector_score,
                "keyword_score": result.keyword_score,
            }
            for result in results
        ],
    }
