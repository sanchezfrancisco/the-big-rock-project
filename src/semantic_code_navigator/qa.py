from __future__ import annotations

from dataclasses import dataclass

from semantic_code_navigator.models import AnswerCitation, SearchResult


@dataclass(frozen=True)
class Answer:
    question: str
    summary: str
    citations: list[AnswerCitation]


def build_answer(question: str, results: list[SearchResult]) -> Answer:
    if not results:
        return Answer(
            question=question,
            summary="No indexed context was found. Run `scn index <repo>` first.",
            citations=[],
        )

    citations = [
        AnswerCitation(
            file_path=result.file_path,
            start_line=result.start_line,
            end_line=result.end_line,
            score=result.score,
        )
        for result in results
    ]
    top = results[0]
    evidence = "; ".join(
        f"{item.file_path}:{item.start_line}-{item.end_line}" for item in results[:3]
    )
    summary = (
        f"The strongest indexed evidence is in {top.file_path}:{top.start_line}-{top.end_line}. "
        f"Review these citations before acting: {evidence}."
    )
    return Answer(question=question, summary=summary, citations=citations)

