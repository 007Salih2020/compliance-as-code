from __future__ import annotations

import httpx
from azure.identity import DefaultAzureCredential

from app.core.config import get_settings
from app.models.schemas import ChatRequest, EmbeddingsRequest


class BackendClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

    def _auth_headers(self) -> dict[str, str]:
        if self.settings.openai_api_key:
            return {"api-key": self.settings.openai_api_key}
        token = self.credential.get_token(self.settings.openai_resource_scope)
        return {"Authorization": f"Bearer {token.token}"}

    def generate_chat_completion(self, payload: ChatRequest) -> dict:
        if self.settings.enable_live_backend:
            return self._generate_live_chat_completion(payload)
        latest_user_message = next(
            (message.content for message in reversed(payload.messages) if message.role == "user"),
            "",
        )
        return {
            "id": "chatcmpl-local-mvp",
            "model": payload.model,
            "deployment_name": payload.deployment_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"MVP gateway approved the request. Echo summary: {latest_user_message[:180]}",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": max(1, len(latest_user_message) // 4), "completion_tokens": 64},
        }

    def generate_embedding(self, payload: EmbeddingsRequest) -> dict:
        if self.settings.enable_live_backend:
            return self._generate_live_embedding(payload)
        vector = [round(((idx + 1) * 0.01), 4) for idx, _ in enumerate(payload.input[:8])]
        return {
            "object": "list",
            "model": payload.model,
            "deployment_name": payload.deployment_name,
            "data": [{"index": 0, "embedding": vector or [0.01, 0.02, 0.03]}],
            "usage": {"prompt_tokens": max(1, len(payload.input) // 4), "total_tokens": max(1, len(payload.input) // 4)},
        }

    def _generate_live_chat_completion(self, payload: ChatRequest) -> dict:
        url = (
            f"{self.settings.openai_backend_url.rstrip('/')}"
            f"/openai/deployments/{payload.deployment_name}/chat/completions"
        )
        body = {
            "messages": [message.model_dump() for message in payload.messages],
            "max_tokens": payload.max_tokens,
        }
        with httpx.Client(timeout=self.settings.default_backend_timeout_seconds) as client:
            response = client.post(
                url,
                params={"api-version": self.settings.openai_api_version},
                headers=self._auth_headers(),
                json=body,
            )
            response.raise_for_status()
            return response.json()

    def _generate_live_embedding(self, payload: EmbeddingsRequest) -> dict:
        url = (
            f"{self.settings.openai_backend_url.rstrip('/')}"
            f"/openai/deployments/{payload.deployment_name}/embeddings"
        )
        body = {"input": payload.input}
        with httpx.Client(timeout=self.settings.default_backend_timeout_seconds) as client:
            response = client.post(
                url,
                params={"api-version": self.settings.openai_api_version},
                headers=self._auth_headers(),
                json=body,
            )
            response.raise_for_status()
            return response.json()
