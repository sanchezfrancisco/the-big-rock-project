from __future__ import annotations

import argparse
from pathlib import Path

from semantic_code_navigator.config import Settings
from semantic_code_navigator.indexer import index_repository
from semantic_code_navigator.qa import build_answer
from semantic_code_navigator.store import IndexStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="scn", description="Semantic Code Navigator")
    parser.add_argument("--index-path", default=".scn/index.sqlite3", help="Local SQLite index path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Index a local Python repository")
    index_parser.add_argument("repo", help="Repository path")

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the local index")
    ask_parser.add_argument("question", help="Question about the indexed code")
    ask_parser.add_argument("--top-k", type=int, default=5, help="Number of citations to retrieve")

    subparsers.add_parser("status", help="Show index status")
    subparsers.add_parser("reset-index", help="Delete and recreate the local index")

    args = parser.parse_args(argv)
    settings = Settings(index_path=Path(args.index_path))

    if args.command == "index":
        summary = index_repository(Path(args.repo), settings)
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
            print(answer.summary)
            print()
            print("Citations:")
            for citation in answer.citations:
                print(
                    f"- {citation.file_path}:{citation.start_line}-{citation.end_line} "
                    f"(score={citation.score:.3f})"
                )
            return 0

        if args.command == "status":
            status = store.status()
            for key, value in status.items():
                print(f"{key}: {value}")
            return 0

        if args.command == "reset-index":
            store.reset()
            print(f"Index reset: {settings.index_path}")
            return 0
    finally:
        store.close()

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

