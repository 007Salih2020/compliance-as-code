from __future__ import annotations

from typing import Annotated

from fastapi import Header, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings


class IdentityContext(BaseModel):
    user_id: str
    app_id: str
    team: str
    roles: list[str]


def parse_identity_header(
    authorization: Annotated[str | None, Header()] = None,
    x_user_id: Annotated[str | None, Header()] = None,
    x_app_id: Annotated[str | None, Header()] = None,
    x_team: Annotated[str | None, Header()] = None,
    x_roles: Annotated[str | None, Header()] = None,
) -> IdentityContext:
    settings = get_settings()
    if not settings.require_auth:
        return IdentityContext(
            user_id=x_user_id or "local.user@contoso.com",
            app_id=x_app_id or "local-dev-app",
            team=x_team or "platform",
            roles=[role.strip() for role in (x_roles or "platform_admin").split(",") if role.strip()],
        )

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    if not x_user_id or not x_app_id or not x_team:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing identity headers for MVP token context",
        )

    return IdentityContext(
        user_id=x_user_id,
        app_id=x_app_id,
        team=x_team,
        roles=[role.strip() for role in (x_roles or "").split(",") if role.strip()],
    )
