from __future__ import annotations

import re
import unicodedata


WORD_RE = re.compile(r"\w+", flags=re.UNICODE)

ES_QUERY_EXPANSIONS = {
    "autenticacion": "authentication login auth",
    "autenticación": "authentication login auth",
    "funcion": "function",
    "función": "function",
    "clase": "class",
    "archivo": "file path",
    "repositorio": "repository repo",
    "vectorial": "vector embedding",
    "indice": "index",
    "índice": "index",
    "cache": "cache embeddings",
    "seguridad": "security secret auth",
    "pruebas": "tests testing",
    "evaluacion": "evaluation eval recall",
    "evaluación": "evaluation eval recall",
}


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def tokenize_text(text: str) -> set[str]:
    normalized = normalize_text(text)
    return set(WORD_RE.findall(normalized))


def expand_query(question: str, language: str) -> str:
    if language != "es":
        return question
    normalized = normalize_text(question)
    tokens = WORD_RE.findall(normalized)
    expansions: list[str] = []
    for token in tokens:
        extra = ES_QUERY_EXPANSIONS.get(token)
        if extra:
            expansions.append(extra)
    if not expansions:
        return question
    return f"{question} {' '.join(expansions)}"

