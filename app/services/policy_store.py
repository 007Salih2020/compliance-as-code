from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.core.config import get_settings
from app.models.schemas import AdminPolicyUpdate, ModelPolicyUpdate
from app.policies.policy_engine import PolicyConfig


class PolicyStore:
    def __init__(self, path: Path | None = None, routing_path: Path | None = None) -> None:
        settings = get_settings()
        self.path = path or settings.policy_config_path
        self.routing_path = routing_path or settings.model_routing_path

    def load_policy_config(self) -> PolicyConfig:
        data = self._load_yaml(self.path)
        return PolicyConfig(
            blocked_code_names=data.get("forbidden_code_names", []),
            blocked_phrases=data.get("blocked_phrases", []),
            warning_phrases=data.get("warning_phrases", []),
        )

    def get_policy_document(self) -> dict[str, Any]:
        return self._load_yaml(self.path)

    def update_policy_document(self, payload: AdminPolicyUpdate) -> dict[str, Any]:
        current = self._load_yaml(self.path)
        updates = payload.model_dump(exclude_none=True)
        current.update(updates)
        self._save_yaml(self.path, current)
        return current

    def get_model_policies(self) -> dict[str, Any]:
        return self._load_yaml(self.routing_path)

    def update_model_policy(self, payload: ModelPolicyUpdate) -> dict[str, Any]:
        current = self._load_yaml(self.routing_path)
        teams = current.setdefault("teams", {})
        teams[payload.team] = {
            "allowed_models": payload.allowed_models,
            "denied_models": payload.denied_models,
        }
        self._save_yaml(self.routing_path, current)
        return current

    def is_model_allowed(self, team: str, model: str) -> bool:
        data = self._load_yaml(self.routing_path)
        team_policy = data.get("teams", {}).get(team, {})
        denied = set(team_policy.get("denied_models", []))
        allowed = set(team_policy.get("allowed_models", []))
        return model not in denied and (not allowed or model in allowed)

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _save_yaml(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(payload, handle, sort_keys=False)
