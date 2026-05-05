from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path

from semantic_code_navigator.config import Settings
from semantic_code_navigator.eval import run_eval, run_tuning, write_report
from semantic_code_navigator.indexer import index_repository
from semantic_code_navigator.qa import build_answer
from semantic_code_navigator.store import IndexStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="scn", description="Semantic Code Navigator")
    parser.add_argument("--index-path", default=".scn/index.sqlite3", help="Local SQLite index path")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Index a local Python repository")
    index_parser.add_argument("repo", help="Repository path")

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the local index")
    ask_parser.add_argument("question", help="Question about the indexed code")
    ask_parser.add_argument("--top-k", type=int, default=5, help="Number of citations to retrieve")
    explain_parser = subparsers.add_parser("explain", help="Explain retrieval ranking for a query")
    explain_parser.add_argument("question", help="Question to inspect ranking details")
    explain_parser.add_argument("--top-k", type=int, default=5, help="Number of ranked chunks to show")

    subparsers.add_parser("status", help="Show index status")
    subparsers.add_parser("reset-index", help="Delete and recreate the local index")
    subparsers.add_parser("doctor", help="Check local runtime and index health")
    subparsers.add_parser("cache-stats", help="Show embedding cache stats")
    cache_prune_parser = subparsers.add_parser("cache-prune", help="Prune embedding cache entries")
    cache_prune_parser.add_argument("--max-entries", type=int, required=True, help="Keep at most N entries")
    eval_parser = subparsers.add_parser("eval", help="Run retrieval evaluation from JSON dataset")
    eval_parser.add_argument("dataset", help="Path to eval dataset JSON file")
    eval_parser.add_argument("--top-k", type=int, default=5, help="Top-k for retrieval metrics")
    eval_parser.add_argument("--report-out", help="Write JSON report to this file path")
    eval_parser.add_argument("--min-recall", type=float, help="Fail if recall@k is below threshold")
    tune_parser = subparsers.add_parser("tune", help="Tune hybrid keyword weight using eval dataset")
    tune_parser.add_argument("dataset", help="Path to eval dataset JSON file")
    tune_parser.add_argument("--top-k", type=int, default=5, help="Top-k for retrieval metrics")
    tune_parser.add_argument(
        "--weights",
        default="0.20,0.35,0.55,0.70",
        help="Comma-separated hybrid weights to test",
    )
    tune_parser.add_argument("--report-out", help="Write tuning report JSON file")

    args = parser.parse_args(argv)
    settings = Settings.from_env(index_path=Path(args.index_path))

    if args.command == "index":
        summary = index_repository(Path(args.repo), settings)
        if args.json:
            print(
                json.dumps(
                    {
                        "repository": summary.repository,
                        "files": summary.files,
                        "chunks": summary.chunks,
                    }
                )
            )
            return 0
        print(f"Indexed: {summary.repository}")
        print(f"Files: {summary.files}")
        print(f"Chunks: {summary.chunks}")
        return 0

    store = IndexStore(settings)
    try:
        if args.command == "ask":
            results = store.search(args.question, top_k=args.top_k)
            store.record_query(args.question)
            answer = build_answer(args.question, results)
            if args.json:
                print(
                    json.dumps(
                        {
                            "question": answer.question,
                            "summary": answer.summary,
                            "citations": [citation.__dict__ for citation in answer.citations],
                        }
                    )
                )
                return 0
            print(answer.summary)
            print()
            print("Citations:")
            for citation in answer.citations:
                print(
                    f"- {citation.file_path}:{citation.start_line}-{citation.end_line} "
                    f"(score={citation.score:.3f})"
                )
            return 0
        if args.command == "explain":
            results = store.search(args.question, top_k=args.top_k)
            payload = {
                "question": args.question,
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
            if args.json:
                print(json.dumps(payload))
                return 0
            print(f"Query: {args.question}")
            print(
                f"Backend={settings.embedding_backend} "
                f"HybridKeywordWeight={settings.hybrid_keyword_weight:.2f}"
            )
            print()
            for result in results:
                print(
                    f"- {result.file_path}:{result.start_line}-{result.end_line} "
                    f"score={result.score:.3f} "
                    f"vector={result.vector_score:.3f} keyword={result.keyword_score:.3f}"
                )
            return 0

        if args.command == "status":
            status = store.status()
            if args.json:
                print(json.dumps(status))
                return 0
            for key, value in status.items():
                print(f"{key}: {value}")
            return 0
        if args.command == "cache-stats":
            stats = store.cache_stats()
            if args.json:
                print(json.dumps(stats))
                return 0
            for key, value in stats.items():
                print(f"{key}: {value}")
            return 0

        if args.command == "reset-index":
            store.reset()
            if args.json:
                print(json.dumps({"index_path": str(settings.index_path), "reset": True}))
                return 0
            print(f"Index reset: {settings.index_path}")
            return 0
        if args.command == "doctor":
            status = store.status()
            health = run_doctor(settings, status)
            if args.json:
                print(json.dumps(health))
                return 0
            for key, value in health.items():
                print(f"{key}: {value}")
            return 0
        if args.command == "eval":
            report = run_eval(Path(args.dataset), settings, top_k=args.top_k)
            if args.report_out:
                write_report(report, Path(args.report_out))
            recall = float(report["summary"]["recall_at_k"])
            failed = args.min_recall is not None and recall < float(args.min_recall)
            if args.json:
                print(json.dumps(report))
                return 1 if failed else 0
            summary = report["summary"]
            print(f"Eval items: {summary['count']}")
            print(f"top_k: {summary['top_k']}")
            print(f"recall@k: {summary['recall_at_k']:.3f}")
            print(f"mean_latency_ms: {summary['mean_latency_ms']:.2f}")
            if args.report_out:
                print(f"report: {args.report_out}")
            if failed:
                print(f"FAIL: recall@k below threshold ({recall:.3f} < {args.min_recall:.3f})")
                return 1
            return 0
        if args.command == "cache-prune":
            result = store.prune_cache(args.max_entries)
            if args.json:
                print(json.dumps(result))
                return 0
            for key, value in result.items():
                print(f"{key}: {value}")
            return 0
        if args.command == "tune":
            weights = [float(item.strip()) for item in args.weights.split(",") if item.strip()]
            report = run_tuning(Path(args.dataset), settings, top_k=args.top_k, weights=weights)
            if args.report_out:
                write_report(report, Path(args.report_out))
            if args.json:
                print(json.dumps(report))
                return 0
            best = report["best"]
            print(f"best_weight: {best['weight']:.2f}")
            print(f"best_recall@k: {best['recall_at_k']:.3f}")
            print(f"best_mean_latency_ms: {best['mean_latency_ms']:.2f}")
            if args.report_out:
                print(f"report: {args.report_out}")
            return 0
    finally:
        store.close()

    parser.error(f"Unknown command: {args.command}")
    return 2


def run_doctor(settings: Settings, status: dict[str, int | str]) -> dict[str, int | str | bool]:
    sqlite_ok = True
    sqlite_error = ""
    try:
        conn = sqlite3.connect(settings.index_path)
        conn.close()
    except sqlite3.Error as exc:
        sqlite_ok = False
        sqlite_error = str(exc)
    provider_ok = True
    provider_error = ""
    if settings.embedding_backend == "openai":
        if not os.getenv("OPENAI_API_KEY", "").strip():
            provider_ok = False
            provider_error = "OPENAI_API_KEY is missing."
        else:
            try:
                import openai  # noqa: F401
            except Exception:
                provider_ok = False
                provider_error = "openai package is not installed. pip install -e '.[providers]'"
    return {
        "python_backend": settings.embedding_backend,
        "provider_ok": provider_ok,
        "provider_error": provider_error,
        "index_exists": settings.index_path.exists(),
        "sqlite_ok": sqlite_ok,
        "sqlite_error": sqlite_error,
        "schema_version": status.get("schema_version", "unknown"),
        "files": int(status.get("files", 0)),
        "chunks": int(status.get("chunks", 0)),
    }


if __name__ == "__main__":
    raise SystemExit(main())
