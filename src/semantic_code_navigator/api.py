from __future__ import annotations

from pathlib import Path
import time

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from semantic_code_navigator.config import Settings
from semantic_code_navigator.eval import run_eval, run_tuning
from semantic_code_navigator.indexer import index_repository
from semantic_code_navigator.metrics import append_metric, read_recent_metrics
from semantic_code_navigator.qa import build_answer
from semantic_code_navigator.store import IndexStore


app = FastAPI(title="Semantic Code Navigator", version="0.1.0")
STATIC_DIR = Path(__file__).resolve().parent / "web"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class IndexRequest(BaseModel):
    repo_path: str
    index_path: str = ".scn/index.sqlite3"
    embedding_backend: str | None = None
    hybrid_keyword_weight: float | None = None
    embedding_cache_path: str | None = None


class AskRequest(BaseModel):
    question: str
    index_path: str = ".scn/index.sqlite3"
    top_k: int = 5
    embedding_backend: str | None = None
    hybrid_keyword_weight: float | None = None
    embedding_cache_path: str | None = None


class ExplainRequest(BaseModel):
    question: str
    index_path: str = ".scn/index.sqlite3"
    top_k: int = 5
    embedding_backend: str | None = None
    hybrid_keyword_weight: float | None = None
    embedding_cache_path: str | None = None


class EvalRequest(BaseModel):
    dataset_path: str
    index_path: str = ".scn/index.sqlite3"
    top_k: int = 5
    embedding_backend: str | None = None
    hybrid_keyword_weight: float | None = None
    embedding_cache_path: str | None = None


class TuneRequest(BaseModel):
    dataset_path: str
    index_path: str = ".scn/index.sqlite3"
    top_k: int = 5
    weights: list[float]
    embedding_backend: str | None = None
    hybrid_keyword_weight: float | None = None
    embedding_cache_path: str | None = None


class CachePruneRequest(BaseModel):
    index_path: str = ".scn/index.sqlite3"
    max_entries: int
    embedding_cache_path: str | None = None


def _settings_from_request(
    index_path: str,
    embedding_backend: str | None = None,
    hybrid_keyword_weight: float | None = None,
    embedding_cache_path: str | None = None,
) -> Settings:
    base = Settings.from_env(index_path=Path(index_path))
    return Settings(
        index_path=base.index_path,
        embedding_cache_path=Path(embedding_cache_path) if embedding_cache_path else base.embedding_cache_path,
        max_file_bytes=base.max_file_bytes,
        vector_dimensions=base.vector_dimensions,
        default_top_k=base.default_top_k,
        embedding_backend=embedding_backend or base.embedding_backend,
        hybrid_keyword_weight=(
            base.hybrid_keyword_weight
            if hybrid_keyword_weight is None
            else max(0.0, min(1.0, hybrid_keyword_weight))
        ),
    )


@app.get("/")
def ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/index")
def index_repo(request: IndexRequest) -> dict[str, int | str]:
    started = time.perf_counter()
    settings = _settings_from_request(
        request.index_path,
        request.embedding_backend,
        request.hybrid_keyword_weight,
        request.embedding_cache_path,
    )
    summary = index_repository(
        Path(request.repo_path),
        settings,
    )
    append_metric(
        "index",
        {
            "repo_path": request.repo_path,
            "index_path": request.index_path,
            "backend": settings.embedding_backend,
            "hybrid_keyword_weight": settings.hybrid_keyword_weight,
            "latency_ms": (time.perf_counter() - started) * 1000.0,
            "files": summary.files,
            "chunks": summary.chunks,
        },
    )
    return {"repository": summary.repository, "files": summary.files, "chunks": summary.chunks}


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, object]:
    started = time.perf_counter()
    settings = _settings_from_request(
        request.index_path,
        request.embedding_backend,
        request.hybrid_keyword_weight,
        request.embedding_cache_path,
    )
    store = IndexStore(settings)
    try:
        results = store.search(request.question, top_k=request.top_k)
        store.record_query(request.question)
    finally:
        store.close()
    answer = build_answer(request.question, results)
    append_metric(
        "ask",
        {
            "index_path": request.index_path,
            "backend": settings.embedding_backend,
            "hybrid_keyword_weight": settings.hybrid_keyword_weight,
            "latency_ms": (time.perf_counter() - started) * 1000.0,
            "question_len": len(request.question),
            "citations": len(answer.citations),
        },
    )
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
    started = time.perf_counter()
    settings = _settings_from_request(
        request.index_path,
        request.embedding_backend,
        request.hybrid_keyword_weight,
        request.embedding_cache_path,
    )
    store = IndexStore(settings)
    try:
        results = store.search(request.question, top_k=request.top_k)
    finally:
        store.close()
    payload = {
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
    append_metric(
        "explain",
        {
            "index_path": request.index_path,
            "backend": settings.embedding_backend,
            "hybrid_keyword_weight": settings.hybrid_keyword_weight,
            "latency_ms": (time.perf_counter() - started) * 1000.0,
            "results": len(payload["results"]),
        },
    )
    return payload


@app.post("/eval")
def eval_dataset(request: EvalRequest) -> dict[str, object]:
    started = time.perf_counter()
    settings = _settings_from_request(
        request.index_path,
        request.embedding_backend,
        request.hybrid_keyword_weight,
        request.embedding_cache_path,
    )
    report = run_eval(Path(request.dataset_path), settings, top_k=request.top_k)
    append_metric(
        "eval",
        {
            "dataset_path": request.dataset_path,
            "index_path": request.index_path,
            "backend": settings.embedding_backend,
            "hybrid_keyword_weight": settings.hybrid_keyword_weight,
            "latency_ms": (time.perf_counter() - started) * 1000.0,
            "recall_at_k": report["summary"]["recall_at_k"],
            "mean_latency_ms": report["summary"]["mean_latency_ms"],
        },
    )
    return report


@app.post("/tune")
def tune_dataset(request: TuneRequest) -> dict[str, object]:
    started = time.perf_counter()
    settings = _settings_from_request(
        request.index_path,
        request.embedding_backend,
        request.hybrid_keyword_weight,
        request.embedding_cache_path,
    )
    report = run_tuning(
        Path(request.dataset_path),
        settings,
        top_k=request.top_k,
        weights=request.weights,
    )
    append_metric(
        "tune",
        {
            "dataset_path": request.dataset_path,
            "index_path": request.index_path,
            "backend": settings.embedding_backend,
            "latency_ms": (time.perf_counter() - started) * 1000.0,
            "best_weight": report["best"]["weight"],
            "best_recall_at_k": report["best"]["recall_at_k"],
        },
    )
    return report


@app.get("/cache/stats")
def cache_stats(index_path: str = ".scn/index.sqlite3") -> dict[str, int | str]:
    store = IndexStore(Settings.from_env(index_path=Path(index_path)))
    try:
        return store.cache_stats()
    finally:
        store.close()


@app.post("/cache/prune")
def cache_prune(request: CachePruneRequest) -> dict[str, int | str]:
    settings = _settings_from_request(
        request.index_path,
        embedding_cache_path=request.embedding_cache_path,
    )
    store = IndexStore(settings)
    try:
        result = store.prune_cache(request.max_entries)
        append_metric(
            "cache_prune",
            {
                "index_path": request.index_path,
                "max_entries": request.max_entries,
                "deleted_entries": result["deleted_entries"],
                "after_entries": result["after_entries"],
            },
        )
        return result
    finally:
        store.close()


@app.get("/metrics/recent")
def metrics_recent(limit: int = 100) -> dict[str, object]:
    return {"items": read_recent_metrics(limit=limit)}


@app.get("/suggest")
def suggest(
    q: str,
    index_path: str = ".scn/index.sqlite3",
    top_k: int = 5,
    embedding_backend: str | None = None,
    hybrid_keyword_weight: float | None = None,
    embedding_cache_path: str | None = None,
) -> dict[str, object]:
    if not q.strip():
        return {"items": []}
    settings = _settings_from_request(
        index_path,
        embedding_backend,
        hybrid_keyword_weight,
        embedding_cache_path,
    )
    store = IndexStore(settings)
    try:
        results = store.search(q, top_k=top_k)
    finally:
        store.close()
    items: list[str] = []
    seen: set[str] = set()
    for result in results:
        if result.symbol:
            candidate = f"Where is {result.symbol} implemented?"
            if candidate not in seen:
                items.append(candidate)
                seen.add(candidate)
        candidate = f"Explain {result.file_path}:{result.start_line}-{result.end_line}"
        if candidate not in seen:
            items.append(candidate)
            seen.add(candidate)
        if len(items) >= top_k:
            break
    return {"items": items}
