from __future__ import annotations

import re

from app.models.schemas import RuleHit

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
CC_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
SECRET_RE = re.compile(
    r"\b(?:api[_-]?key|password|secret|token|client[_-]?secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{6,}",
    re.IGNORECASE,
)


def detect_pii_and_secrets(text: str) -> list[RuleHit]:
    hits: list[RuleHit] = []
    for match in EMAIL_RE.findall(text):
        hits.append(RuleHit(rule_id="pii.email", category="pii", severity="medium", match=match, score=20))
    for match in CC_RE.findall(text):
        hits.append(
            RuleHit(rule_id="pii.credit_card_like", category="pii", severity="high", match=match, score=50)
        )
    for match in SECRET_RE.findall(text):
        hits.append(
            RuleHit(rule_id="secret.credential_pattern", category="secret", severity="high", match=match, score=60)
        )
    return hits
