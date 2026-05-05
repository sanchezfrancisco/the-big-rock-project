from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from semantic_code_navigator.config import Settings
from semantic_code_navigator.store import IndexStore


@dataclass(frozen=True)
class EvalItemResult:
    question: str
    expected_files: list[str]
    hits: int
    total_expected: int
    top_k: int
    latency_ms: float


def run_eval(eval_file: Path, settings: Settings, top_k: int) -> dict[str, object]:
    payload = json.loads(eval_file.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    store = IndexStore(settings)
    try:
        results: list[EvalItemResult] = []
        for item in items:
            question = str(item["question"])
            expected_files = [str(path) for path in item.get("expected_files", [])]
            started = time.perf_counter()
            found = store.search(question, top_k=top_k)
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            found_paths = {entry.file_path for entry in found}
            hits = sum(1 for path in expected_files if path in found_paths)
            results.append(
                EvalItemResult(
                    question=question,
                    expected_files=expected_files,
                    hits=hits,
                    total_expected=len(expected_files),
                    top_k=top_k,
                    latency_ms=elapsed_ms,
                )
            )
    finally:
        store.close()

    total_expected = sum(item.total_expected for item in results)
    total_hits = sum(item.hits for item in results)
    recall_at_k = (total_hits / total_expected) if total_expected else 0.0
    mean_latency_ms = (
        sum(item.latency_ms for item in results) / len(results) if results else 0.0
    )
    return {
        "items": [
            {
                "question": item.question,
                "expected_files": item.expected_files,
                "hits": item.hits,
                "total_expected": item.total_expected,
                "latency_ms": item.latency_ms,
            }
            for item in results
        ],
        "summary": {
            "count": len(results),
            "top_k": top_k,
            "recall_at_k": recall_at_k,
            "mean_latency_ms": mean_latency_ms,
        },
    }

