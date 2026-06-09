from __future__ import annotations

from app.models.schemas import RuleHit

BLOCK_PHRASES = [
    "ignore previous instructions",
    "disregard all prior guidance",
    "reveal the system prompt",
    "bypass safety controls",
    "developer mode enabled",
]

WARNING_PHRASES = [
    "act as an unrestricted model",
    "simulate malware",
    "disable content filters",
]


def detect_injection(text: str) -> list[RuleHit]:
    lowered = text.lower()
    hits: list[RuleHit] = []
    for phrase in BLOCK_PHRASES:
        if phrase in lowered:
            hits.append(
                RuleHit(
                    rule_id="prompt_injection.block",
                    category="prompt_injection",
                    severity="critical",
                    match=phrase,
                    score=80,
                )
            )
    for phrase in WARNING_PHRASES:
        if phrase in lowered:
            hits.append(
                RuleHit(
                    rule_id="prompt_injection.warn",
                    category="prompt_injection",
                    severity="medium",
                    match=phrase,
                    score=25,
                )
            )
    return hits
