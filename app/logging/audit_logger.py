from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.models.schemas import AuditEvent, PolicyDecision


class AuditLogger:
    def __init__(self, path: Path | None = None) -> None:
        settings = get_settings()
        self.path = path or settings.audit_log_path

    def prompt_hash(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def write_event(
        self,
        *,
        user_id: str,
        app_id: str,
        team: str,
        model: str,
        deployment_name: str,
        prompt: str,
        decision: PolicyDecision,
        estimated_tokens: int,
        latency_ms: int,
        response_status: int,
        correlation_id: str,
        action: str,
        route: str,
        timestamp: datetime | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            timestamp=timestamp or datetime.now(UTC),
            user_id=user_id,
            app_id=app_id,
            team=team,
            model=model,
            deployment_name=deployment_name,
            prompt_hash=self.prompt_hash(prompt),
            decision=decision.decision,
            rule_hits=decision.rule_hits,
            estimated_tokens=estimated_tokens,
            latency_ms=latency_ms,
            response_status=response_status,
            correlation_id=correlation_id,
            action=action,
            route=route,
            warning_count=sum(1 for hit in decision.rule_hits if hit.severity in {"medium", "high"}),
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.model_dump(mode="json")) + "\n")
        return event

    def clear_events(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def recent_blocked(self, limit: int = 25) -> list[dict[str, Any]]:
        entries = self._read_lines()
        blocked = [entry for entry in entries if entry.get("decision") == "block"]
        return blocked[-limit:]

    def usage_summary(self) -> dict[str, Any]:
        entries = self._read_lines()
        by_team: dict[str, int] = {}
        by_model: dict[str, int] = {}
        for entry in entries:
            by_team[entry["team"]] = by_team.get(entry["team"], 0) + entry.get("estimated_tokens", 0)
            by_model[entry["model"]] = by_model.get(entry["model"], 0) + 1
        return {"events": len(entries), "tokens_by_team": by_team, "requests_by_model": by_model}

    def _read_lines(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
