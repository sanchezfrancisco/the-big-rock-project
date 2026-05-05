from __future__ import annotations

import hashlib
import math
import os
import re


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")


def embedding_model_for_backend(backend: str) -> str:
    if backend == "openai":
        return os.getenv("SCN_OPENAI_EMBED_MODEL", "text-embedding-3-small")
    return "local-hash-v1"


def embed_text(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    for token in TOKEN_RE.findall(text.lower()):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def embed_text_with_backend(text: str, dimensions: int, backend: str = "local") -> list[float]:
    if backend == "local":
        return embed_text(text, dimensions)
    if backend == "openai":
        return _embed_text_openai(text, dimensions)
    raise ValueError(
        f"Unsupported embedding backend '{backend}'. "
        "Use 'local' or 'openai'."
    )


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def _embed_text_openai(text: str, dimensions: int) -> list[float]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required when SCN_EMBEDDING_BACKEND=openai.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ValueError(
            "OpenAI provider is not installed. Run: pip install -e '.[providers]'"
        ) from exc
    client = OpenAI(api_key=api_key)
    model = os.getenv("SCN_OPENAI_EMBED_MODEL", "text-embedding-3-small")
    response = client.embeddings.create(model=model, input=text)
    raw = response.data[0].embedding
    if not raw:
        return [0.0] * dimensions
    if len(raw) == dimensions:
        return [float(v) for v in raw]
    # Project deterministicly to configured dimensions.
    projected = [0.0] * dimensions
    for i, value in enumerate(raw):
        projected[i % dimensions] += float(value)
    norm = math.sqrt(sum(v * v for v in projected))
    if norm == 0:
        return projected
    return [v / norm for v in projected]
