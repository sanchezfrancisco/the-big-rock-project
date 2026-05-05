from __future__ import annotations

import hashlib
import math
import re


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")


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
    raise ValueError(
        f"Unsupported embedding backend '{backend}'. "
        "Use 'local' or install an external provider backend."
    )


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))
