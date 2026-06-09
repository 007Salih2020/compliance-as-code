from __future__ import annotations

from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.auth import IdentityContext, parse_identity_header
from app.models.schemas import ChatRequest, EmbeddingsRequest, PolicyDecision
from app.policies.policy_engine import PolicyEngine
from app.services.runtime import audit_logger, backend_client, policy_store, quota_service
from app.services.response_inspector import redact_response

router = APIRouter()


def _build_engine() -> PolicyEngine:
    return PolicyEngine(policy_store.load_policy_config())


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _log_event(
    *,
    identity: IdentityContext,
    model: str,
    deployment_name: str,
    prompt: str,
    decision: PolicyDecision,
    latency_ms: int,
    response_status: int,
    correlation_id: str,
    route: str,
) -> None:
    audit_logger.write_event(
        user_id=identity.user_id,
        app_id=identity.app_id,
        team=identity.team,
        model=model,
        deployment_name=deployment_name,
        prompt=prompt,
        decision=decision,
        estimated_tokens=_estimate_tokens(prompt),
        latency_ms=latency_ms,
        response_status=response_status,
        correlation_id=correlation_id,
        action="enforce",
        route=route,
    )


@router.post("/chat")
def chat_completion(
    payload: ChatRequest,
    identity: Annotated[IdentityContext, Depends(parse_identity_header)],
    x_correlation_id: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    started = perf_counter()
    correlation_id = x_correlation_id or str(uuid4())
    prompt_text = "\n".join(message.content for message in payload.messages)
    if payload.team and payload.team != identity.team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Team override is not allowed")
    if payload.app_id and payload.app_id != identity.app_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="App override is not allowed")
    effective_team = identity.team

    if len(prompt_text) > 16000:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Prompt too large")

    if not policy_store.is_model_allowed(effective_team, payload.model):
        decision = PolicyDecision(decision="block", reasons=["Model is not allowed for team"])
        _log_event(
            identity=identity,
            model=payload.model,
            deployment_name=payload.deployment_name,
            prompt=prompt_text,
            decision=decision,
            latency_ms=int((perf_counter() - started) * 1000),
            response_status=status.HTTP_403_FORBIDDEN,
            correlation_id=correlation_id,
            route="/chat",
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Model not allowed")

    quota = quota_service.check_and_consume(effective_team, identity.user_id)
    if not quota.allowed:
        decision = PolicyDecision(decision="block", reasons=[quota.reason or "Quota exceeded"])
        _log_event(
            identity=identity,
            model=payload.model,
            deployment_name=payload.deployment_name,
            prompt=prompt_text,
            decision=decision,
            latency_ms=int((perf_counter() - started) * 1000),
            response_status=status.HTTP_429_TOO_MANY_REQUESTS,
            correlation_id=correlation_id,
            route="/chat",
        )
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=quota.reason)

    engine = _build_engine()
    prompt_decision = engine.inspect_prompt(prompt_text)
    if prompt_decision.decision == "block":
        _log_event(
            identity=identity,
            model=payload.model,
            deployment_name=payload.deployment_name,
            prompt=prompt_text,
            decision=prompt_decision,
            latency_ms=int((perf_counter() - started) * 1000),
            response_status=status.HTTP_403_FORBIDDEN,
            correlation_id=correlation_id,
            route="/chat",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"decision": prompt_decision.decision, "rule_hits": [hit.model_dump() for hit in prompt_decision.rule_hits]},
        )

    backend_response = backend_client.generate_chat_completion(payload)
    assistant_content = backend_response["choices"][0]["message"]["content"]
    response_decision = engine.inspect_response(assistant_content)
    backend_response["choices"][0]["message"]["content"] = redact_response(assistant_content)
    backend_response["policy_decision"] = prompt_decision.model_dump()
    backend_response["response_policy_decision"] = response_decision.model_dump()
    latency_ms = int((perf_counter() - started) * 1000)
    _log_event(
        identity=identity,
        model=payload.model,
        deployment_name=payload.deployment_name,
        prompt=prompt_text,
        decision=prompt_decision,
        latency_ms=latency_ms,
        response_status=status.HTTP_200_OK,
        correlation_id=correlation_id,
        route="/chat",
    )
    return JSONResponse(
        content=backend_response,
        headers={"x-correlation-id": correlation_id},
    )


@router.post("/embeddings")
def embeddings(
    payload: EmbeddingsRequest,
    identity: Annotated[IdentityContext, Depends(parse_identity_header)],
    x_correlation_id: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    started = perf_counter()
    correlation_id = x_correlation_id or str(uuid4())
    if payload.team and payload.team != identity.team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Team override is not allowed")
    if payload.app_id and payload.app_id != identity.app_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="App override is not allowed")
    effective_team = identity.team

    if not policy_store.is_model_allowed(effective_team, payload.model):
        decision = PolicyDecision(decision="block", reasons=["Model is not allowed for team"])
        _log_event(
            identity=identity,
            model=payload.model,
            deployment_name=payload.deployment_name,
            prompt=payload.input,
            decision=decision,
            latency_ms=int((perf_counter() - started) * 1000),
            response_status=status.HTTP_403_FORBIDDEN,
            correlation_id=correlation_id,
            route="/embeddings",
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Model not allowed")

    prompt_decision = _build_engine().inspect_prompt(payload.input)
    if prompt_decision.decision == "block":
        _log_event(
            identity=identity,
            model=payload.model,
            deployment_name=payload.deployment_name,
            prompt=payload.input,
            decision=prompt_decision,
            latency_ms=int((perf_counter() - started) * 1000),
            response_status=status.HTTP_403_FORBIDDEN,
            correlation_id=correlation_id,
            route="/embeddings",
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Embedding input blocked")

    result = backend_client.generate_embedding(payload)
    _log_event(
        identity=identity,
        model=payload.model,
        deployment_name=payload.deployment_name,
        prompt=payload.input,
        decision=prompt_decision,
        latency_ms=int((perf_counter() - started) * 1000),
        response_status=status.HTTP_200_OK,
        correlation_id=correlation_id,
        route="/embeddings",
    )
    return JSONResponse(
        content=result,
        headers={"x-correlation-id": correlation_id},
    )
