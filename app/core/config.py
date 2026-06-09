from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    app_name: str = Field(default="Ozkan Gateway")
    environment: str = Field(default="dev")
    log_level: str = Field(default="INFO")
    audit_log_path: Path = Field(default=Path("artifacts/audit-log.jsonl"))
    policy_config_path: Path = Field(default=Path("config/policies.yaml"))
    model_routing_path: Path = Field(default=Path("config/model_routing.yaml"))
    quota_config_path: Path = Field(default=Path("config/quotas.yaml"))
    enable_live_backend: bool = Field(default=False)
    require_auth: bool = Field(default=False)
    entra_tenant_id: str = Field(default="")
    entra_audience: str = Field(default="api://ozkan-gateway")
    openai_backend_url: str = Field(default="https://example.openai.azure.com")
    openai_api_version: str = Field(default="2024-10-21")
    openai_resource_scope: str = Field(default="https://cognitiveservices.azure.com/.default")
    openai_api_key: str = Field(default="")
    default_backend_timeout_seconds: int = Field(default=15)
    blocked_code_names: list[str] = Field(default_factory=list)


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@lru_cache
def get_settings() -> Settings:
    raw_code_names = os.getenv("BLOCKED_CODE_NAMES", "")
    blocked_code_names = [item.strip() for item in raw_code_names.split(",") if item.strip()]
    return Settings(
        app_name=os.getenv("APP_NAME", "Ozkan Gateway"),
        environment=os.getenv("ENVIRONMENT", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        audit_log_path=Path(os.getenv("AUDIT_LOG_PATH", "artifacts/audit-log.jsonl")),
        policy_config_path=Path(os.getenv("POLICY_CONFIG_PATH", "config/policies.yaml")),
        model_routing_path=Path(os.getenv("MODEL_ROUTING_PATH", "config/model_routing.yaml")),
        quota_config_path=Path(os.getenv("QUOTA_CONFIG_PATH", "config/quotas.yaml")),
        enable_live_backend=_parse_bool(os.getenv("ENABLE_LIVE_BACKEND"), False),
        require_auth=_parse_bool(os.getenv("REQUIRE_AUTH"), False),
        entra_tenant_id=os.getenv("ENTRA_TENANT_ID", ""),
        entra_audience=os.getenv("ENTRA_AUDIENCE", "api://ozkan-gateway"),
        openai_backend_url=os.getenv("OPENAI_BACKEND_URL", "https://example.openai.azure.com"),
        openai_api_version=os.getenv("OPENAI_API_VERSION", "2024-10-21"),
        openai_resource_scope=os.getenv(
            "OPENAI_RESOURCE_SCOPE",
            "https://cognitiveservices.azure.com/.default",
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        default_backend_timeout_seconds=int(os.getenv("DEFAULT_BACKEND_TIMEOUT_SECONDS", "15")),
        blocked_code_names=blocked_code_names,
    )
