from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from semantic_code_navigator.models import AnswerCitation, SearchResult


@dataclass(frozen=True)
class Answer:
    question: str
    summary: str
    citations: list[AnswerCitation]


def build_answer(question: str, results: list[SearchResult]) -> Answer:
    return build_answer_with_language(question, results, language="en")


def build_answer_with_language(question: str, results: list[SearchResult], language: str = "en") -> Answer:
    if not results:
        summary = "No indexed context was found. Run `scn index <repo>` first."
        if language == "es":
            summary = "No se encontro contexto indexado. Ejecuta `scn index <repo>` primero."
        return Answer(
            question=question,
            summary=summary,
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
    direct = _direct_answer(question, results, language)
    flow = _flow_summary(results[:5], language)
    if language == "es":
        base = (
            f"La evidencia indexada mas fuerte esta en {top.file_path}:{top.start_line}-{top.end_line}. "
            f"Revisa estas citas antes de actuar: {evidence}."
        )
        summary = f"{direct}\n\n{flow}\n\n{base}" if direct else f"{flow}\n\n{base}"
    else:
        base = (
            f"The strongest indexed evidence is in {top.file_path}:{top.start_line}-{top.end_line}. "
            f"Review these citations before acting: {evidence}."
        )
        summary = f"{direct}\n\n{flow}\n\n{base}" if direct else f"{flow}\n\n{base}"
    return Answer(question=question, summary=summary, citations=citations)


def _direct_answer(question: str, results: list[SearchResult], language: str) -> str:
    q = question.lower()
    if _contains_any(q, ["pasarela", "pago", "stripe", "payment", "gateway"]):
        provider = _detect_provider(results)
        has_signal = provider is not None or any(_contains_any(r.content.lower(), ["payment", "pago", "checkout", "gateway"]) for r in results)
        if language == "es":
            if has_signal:
                if provider:
                    return f"Si. El sistema muestra evidencia de pasarela de pago y el proveedor mas probable es {provider}."
                return "Si. El sistema muestra evidencia de una pasarela o flujo de pago en el codigo indexado."
            return "No hay evidencia suficiente de una pasarela de pago en el indice actual."
        if has_signal:
            if provider:
                return f"Yes. The system shows payment-gateway evidence and the most likely provider is {provider}."
            return "Yes. The system shows evidence of a payment workflow in the indexed code."
        return "There is not enough evidence of a payment gateway in the current index."
    return ""


def _flow_summary(results: Iterable[SearchResult], language: str) -> str:
    ordered = list(results)[:4]
    if not ordered:
        return ""
    lines: list[str] = []
    for idx, item in enumerate(ordered, start=1):
        if language == "es":
            lines.append(
                f"{idx}. Revisar `{item.file_path}` lineas {item.start_line}-{item.end_line}"
                + (f" (simbolo: {item.symbol})" if item.symbol else "")
            )
        else:
            lines.append(
                f"{idx}. Inspect `{item.file_path}` lines {item.start_line}-{item.end_line}"
                + (f" (symbol: {item.symbol})" if item.symbol else "")
            )
    if language == "es":
        return "Flujo sugerido a partir de la evidencia:\n" + "\n".join(lines)
    return "Suggested flow from the evidence:\n" + "\n".join(lines)


def _detect_provider(results: list[SearchResult]) -> str | None:
    corpus = "\n".join(item.content.lower() for item in results[:10])
    providers = ["stripe", "paypal", "mercadopago", "adyen", "square"]
    for provider in providers:
        if provider in corpus:
            return provider
    return None


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)
