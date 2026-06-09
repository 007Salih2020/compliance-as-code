# Local Development Guide

## Quick start
1. `python3 -m pip install -e ".[dev]"`
2. `cp .env.example .env`
3. `uvicorn app.main:app --reload --port 8080`
4. `streamlit run ui.py --server.port 8501`

## Notes
- Local mode defaults `REQUIRE_AUTH=false`, so identity is supplied via headers.
- The backend client is a stub that returns deterministic responses for testing.
- If `ENABLE_LIVE_BACKEND=true`, the backend will call Azure OpenAI using `OPENAI_API_KEY` or managed identity via `DefaultAzureCredential`.
- Policies and quotas are file-backed YAML documents in `config/`.
- Audit logs are written to `artifacts/audit-log.jsonl`.
- The Streamlit console uses `UI_BACKEND_URL` from `.env` and is intended for internal admin/demo use.

## Quality checks
- `make lint`
- `make test`
