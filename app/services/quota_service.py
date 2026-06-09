from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from app.core.config import get_settings
from app.models.schemas import QuotaStatus, QuotaUpdate


class QuotaService:
    def __init__(self, quota_path: Path | None = None) -> None:
        settings = get_settings()
        self.quota_path = quota_path or settings.quota_config_path
        self.team_events: dict[str, deque[datetime]] = defaultdict(deque)
        self.user_events: dict[str, deque[datetime]] = defaultdict(deque)

    def check_and_consume(self, team: str, user_id: str) -> QuotaStatus:
        config = self._load_yaml()
        team_config = config.get("teams", {}).get(team, config.get("default", {}))
        now = datetime.now(UTC)
        self._prune(self.team_events[team], now)
        self._prune(self.user_events[user_id], now)

        team_minute_limit = int(team_config.get("per_minute_limit", 60))
        user_minute_limit = int(team_config.get("per_user_per_minute_limit", 20))

        if len(self.team_events[team]) >= team_minute_limit:
            return QuotaStatus(
                allowed=False,
                reason="Team minute quota exceeded",
                team_usage=len(self.team_events[team]),
                team_limit=team_minute_limit,
                user_usage=len(self.user_events[user_id]),
                user_limit=user_minute_limit,
            )
        if len(self.user_events[user_id]) >= user_minute_limit:
            return QuotaStatus(
                allowed=False,
                reason="User minute quota exceeded",
                team_usage=len(self.team_events[team]),
                team_limit=team_minute_limit,
                user_usage=len(self.user_events[user_id]),
                user_limit=user_minute_limit,
            )

        self.team_events[team].append(now)
        self.user_events[user_id].append(now)
        return QuotaStatus(
            allowed=True,
            team_usage=len(self.team_events[team]),
            team_limit=team_minute_limit,
            user_usage=len(self.user_events[user_id]),
            user_limit=user_minute_limit,
        )

    def get_document(self) -> dict[str, Any]:
        return self._load_yaml()

    def update_team_quota(self, payload: QuotaUpdate) -> dict[str, Any]:
        current = self._load_yaml()
        teams = current.setdefault("teams", {})
        team_entry = teams.setdefault(payload.team, {})
        team_entry["per_minute_limit"] = payload.per_minute_limit
        team_entry["per_day_limit"] = payload.per_day_limit
        team_entry.setdefault("per_user_per_minute_limit", max(1, payload.per_minute_limit // 3))
        self._save_yaml(current)
        return current

    def clear_usage(self) -> None:
        self.team_events.clear()
        self.user_events.clear()

    def seed_usage(self, *, team_usage: dict[str, int], user_usage: dict[str, int]) -> dict[str, Any]:
        self.clear_usage()
        now = datetime.now(UTC)
        for team, count in team_usage.items():
            self._seed_counter(self.team_events[team], count, now)
        for user_id, count in user_usage.items():
            self._seed_counter(self.user_events[user_id], count, now)
        return self.usage_summary()

    def usage_summary(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        for events in self.team_events.values():
            self._prune(events, now)
        for events in self.user_events.values():
            self._prune(events, now)
        return {
            "team_usage_last_minute": {team: len(events) for team, events in self.team_events.items() if events},
            "user_usage_last_minute": {user_id: len(events) for user_id, events in self.user_events.items() if events},
        }

    def _prune(self, items: deque[datetime], now: datetime) -> None:
        cutoff = now - timedelta(minutes=1)
        while items and items[0] < cutoff:
            items.popleft()

    def _seed_counter(self, items: deque[datetime], count: int, now: datetime) -> None:
        items.clear()
        for index in range(max(0, count)):
            seconds_ago = max(1, min(59, count - index))
            items.append(now - timedelta(seconds=seconds_ago))

    def _load_yaml(self) -> dict[str, Any]:
        with self.quota_path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _save_yaml(self, payload: dict[str, Any]) -> None:
        self.quota_path.parent.mkdir(parents=True, exist_ok=True)
        with self.quota_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(payload, handle, sort_keys=False)
