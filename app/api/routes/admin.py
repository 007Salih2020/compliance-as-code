from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.auth import IdentityContext, parse_identity_header
from app.models.schemas import AdminPolicyUpdate, DemoDataRequest, ModelPolicyUpdate, QuotaUpdate
from app.services.demo_data import DemoDataService
from app.services.runtime import audit_logger, policy_store, quota_service

router = APIRouter()
demo_data_service = DemoDataService(audit_logger=audit_logger, quota_service=quota_service)


def require_admin(identity: Annotated[IdentityContext, Depends(parse_identity_header)]) -> IdentityContext:
    if not {"platform_admin", "security_admin"}.intersection(identity.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return identity


@router.get("/policies")
def get_policies(_: Annotated[IdentityContext, Depends(require_admin)]) -> dict:
    return policy_store.get_policy_document()


@router.put("/policies")
def update_policies(
    payload: AdminPolicyUpdate,
    _: Annotated[IdentityContext, Depends(require_admin)],
) -> dict:
    return policy_store.update_policy_document(payload)


@router.get("/quotas")
def get_quotas(_: Annotated[IdentityContext, Depends(require_admin)]) -> dict:
    return quota_service.get_document()


@router.put("/quotas")
def update_quotas(
    payload: QuotaUpdate,
    _: Annotated[IdentityContext, Depends(require_admin)],
) -> dict:
    return quota_service.update_team_quota(payload)


@router.get("/model-access")
def get_model_access(_: Annotated[IdentityContext, Depends(require_admin)]) -> dict:
    return policy_store.get_model_policies()


@router.put("/model-access")
def update_model_access(
    payload: ModelPolicyUpdate,
    _: Annotated[IdentityContext, Depends(require_admin)],
) -> dict:
    return policy_store.update_model_policy(payload)


@router.get("/blocked-requests")
def blocked_requests(_: Annotated[IdentityContext, Depends(require_admin)]) -> dict:
    return {"items": audit_logger.recent_blocked()}


@router.get("/usage-summary")
def usage_summary(_: Annotated[IdentityContext, Depends(require_admin)]) -> dict:
    return {
        "quota_usage": quota_service.usage_summary(),
        "audit_usage": audit_logger.usage_summary(),
    }


@router.post("/demo-data")
def seed_demo_data(
    payload: DemoDataRequest,
    _: Annotated[IdentityContext, Depends(require_admin)],
) -> dict:
    return demo_data_service.seed(replace_existing=payload.replace_existing)


@router.get("/dashboard", response_class=Response)
def dashboard(_: Annotated[IdentityContext, Depends(require_admin)]) -> Response:
    summary = audit_logger.usage_summary()
    html = f"""
    <html>
      <head><title>Ozkan Admin</title></head>
      <body>
        <h1>Ozkan Admin Dashboard</h1>
        <p>Total events: {summary.get("events", 0)}</p>
        <pre>{summary}</pre>
      </body>
    </html>
    """
    return Response(content=html, media_type="text/html")
