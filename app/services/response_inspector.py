from __future__ import annotations

import re

SECRET_VALUE_RE = re.compile(r"(api[_-]?key|password|token|secret)\s*[:=]\s*([^\s,;]+)", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b([A-Z0-9._%+-]{2})[A-Z0-9._%+-]*@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.IGNORECASE)


def redact_response(text: str) -> str:
    text = SECRET_VALUE_RE.sub(r"\1=[REDACTED]", text)
    text = EMAIL_RE.sub(r"\1***@\2", text)
    return text
