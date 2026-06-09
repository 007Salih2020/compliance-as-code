from __future__ import annotations

from dataclasses import dataclass

from app.models.schemas import PolicyDecision, RuleHit
from app.policies.injection_detector import detect_injection
from app.policies.pii_detector import detect_pii_and_secrets


@dataclass
class PolicyConfig:
    blocked_code_names: list[str]
    blocked_phrases: list[str]
    warning_phrases: list[str]


class PolicyEngine:
    def __init__(self, config: PolicyConfig) -> None:
        self.config = config

    def inspect_prompt(self, text: str) -> PolicyDecision:
        hits: list[RuleHit] = []
        hits.extend(detect_pii_and_secrets(text))
        hits.extend(detect_injection(text))

        lowered = text.lower()
        for code_name in self.config.blocked_code_names:
            if code_name.lower() in lowered:
                hits.append(
                    RuleHit(
                        rule_id="internal.code_name",
                        category="sensitive_internal",
                        severity="high",
                        match=code_name,
                        score=40,
                    )
                )

        for phrase in self.config.blocked_phrases:
            if phrase.lower() in lowered:
                hits.append(
                    RuleHit(
                        rule_id="custom.block_phrase",
                        category="custom",
                        severity="high",
                        match=phrase,
                        score=60,
                    )
                )

        for phrase in self.config.warning_phrases:
            if phrase.lower() in lowered:
                hits.append(
                    RuleHit(
                        rule_id="custom.warning_phrase",
                        category="custom",
                        severity="medium",
                        match=phrase,
                        score=15,
                    )
                )

        total_score = sum(hit.score for hit in hits)
        if any(hit.severity == "critical" for hit in hits) or total_score >= 80:
            return PolicyDecision(
                decision="block",
                rule_hits=hits,
                reasons=["Prompt violated blocking policy"],
                total_score=total_score,
            )
        if hits:
            return PolicyDecision(
                decision="allow_with_warning",
                rule_hits=hits,
                reasons=["Prompt triggered warning controls"],
                total_score=total_score,
            )
        return PolicyDecision(decision="allow", total_score=0)

    def inspect_response(self, text: str) -> PolicyDecision:
        hits = detect_pii_and_secrets(text)
        total_score = sum(hit.score for hit in hits)
        if total_score >= 60:
            return PolicyDecision(
                decision="block",
                rule_hits=hits,
                reasons=["Response contained redaction-worthy content"],
                total_score=total_score,
            )
        if hits:
            return PolicyDecision(
                decision="allow_with_warning",
                rule_hits=hits,
                reasons=["Response contained moderate risk indicators"],
                total_score=total_score,
            )
        return PolicyDecision(decision="allow", total_score=0)
