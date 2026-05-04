from __future__ import annotations

import re
from dataclasses import dataclass


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-.]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
]


@dataclass(frozen=True)
class SecretScanResult:
    redacted_text: str
    findings: int


def redact_secrets(text: str) -> SecretScanResult:
    findings = 0
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted, count = pattern.subn("[REDACTED_SECRET]", redacted)
        findings += count
    return SecretScanResult(redacted_text=redacted, findings=findings)

