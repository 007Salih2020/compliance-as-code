# Ozkan Gateway – Enterprise AI Security Gateway for Azure OpenAI / Azure AI Foundry

## 1. Executive summary
Ozkan Gateway is a production-style MVP for a centralized AI Security Gateway that places Azure API Management in front of Azure OpenAI or Azure AI Foundry and enforces identity, model governance, quota controls, prompt and response inspection, and compliance-grade audit logging. The repository includes a working FastAPI policy and admin service, sample APIM policies, Bicep infrastructure, CI/CD definitions, test stubs, and a demo narrative suitable for security leadership review.

## 2. Why this project matters to a CISO
Direct, decentralized LLM consumption creates unmanaged data exposure, inconsistent access control, weak telemetry, and unclear accountability. This gateway shifts the control point to a governed front door where Microsoft Entra ID, APIM policy, managed identity, logging, and inspection logic provide a measurable control plane. It reduces shadow AI risk, improves auditability, and establishes an extensible pattern for policy enforcement before enterprise adoption scales.

## 3. MVP scope and non-goals
In scope:
- APIM front door for `/chat`, `/embeddings`, and `/admin`.
- Entra ID aligned authentication flow with JWT validation expected at APIM and identity context passed to the app.
- Deterministic prompt inspection for PII, secrets, jailbreaks, injection phrases, and forbidden internal code names.
- Response inspection and lightweight redaction.
- Model allow and deny controls by team.
- Quota and rate-limit enforcement.
- Audit logging with hashes instead of raw prompt storage.
- Admin API for policy, quota, model-access, blocked-request, and usage operations.
- Streamlit governance console for gateway testing and audit visibility.
- Sample Bicep, APIM policy fragments, GitHub Actions, Azure DevOps, Postman, and tests.
- Dockerfile, `.dockerignore`, and container registry deployment path.

Non-goals:
- Full JWT signature validation inside the Python app.
- Direct live forwarding to Azure OpenAI in local mode.
- Production-grade distributed quota storage.
- Full Purview, Defender for Cloud, and Content Safety integration.
- Fine-tuned chargeback accounting or tenant-wide policy lifecycle workflows.

## 4. Target architecture
Client applications authenticate with Microsoft Entra ID and call Azure API Management over HTTPS. APIM validates JWTs, attaches correlation headers, applies coarse rate limits, and forwards requests to the FastAPI gateway running on Azure Container Apps or App Service with managed identity. The gateway applies model policy, prompt inspection, quota checks, and response inspection, then forwards approved requests to Azure OpenAI or Azure AI Foundry using managed identity where available. Logs and metrics flow to Application Insights and Log Analytics. Secrets, only when unavoidable, reside in Key Vault. Private endpoints and VNET integration isolate the control plane and model endpoints from public exposure.

## 5. Architecture diagram description in text
1. Internal user or service obtains an Entra token.
2. Caller sends HTTPS request to APIM.
3. APIM validates the token, rate limits, injects `x-correlation-id`, and forwards to the gateway app.
4. Gateway app derives identity context, loads policy and quota configuration, and inspects prompt content.
5. If blocked, the gateway returns a policy denial and writes an audit event.
6. If allowed, the gateway calls Azure OpenAI or AI Foundry.
7. Gateway inspects and redacts the response when needed, emits audit telemetry, and returns to APIM.
8. APIM returns the final response to the client and emits diagnostics to Log Analytics.

## 6. Trust boundaries and data flows
- Boundary 1: Internal caller to APIM. Authentication boundary. Untrusted input enters the system.
- Boundary 2: APIM to gateway app. Controlled service-to-service traffic inside Azure network boundaries.
- Boundary 3: Gateway app to Azure OpenAI or AI Foundry. Managed identity and approved model policy boundary.
- Boundary 4: Gateway and APIM to observability stack. Audit and operational telemetry boundary.
- Boundary 5: Admin operators to admin API. Elevated governance actions boundary.

Primary data flows:
- Prompt payload, metadata, token claims, quota counters, audit events, and redacted response payloads.

## 7. Azure resource inventory
- Azure API Management
- Azure OpenAI or Azure AI Foundry account and deployments
- Azure Container Apps Environment or Azure App Service Plan
- Azure Container App or App Service for the FastAPI gateway
- Optional Azure Container App for the Streamlit governance UI
- User-assigned managed identity for APIM and gateway
- Azure Key Vault
- Azure Log Analytics workspace
- Azure Application Insights
- Azure Virtual Network with delegated/private subnets
- Private Endpoints for Azure OpenAI, Key Vault, and optionally Container Apps environment ingress
- Azure Monitor alerts and action groups
- Azure Container Registry
- Resource groups for `dev`, `test`, and `prod`

## 8. Security control matrix
| Control Objective | MVP Mechanism | Azure Service |
| --- | --- | --- |
| Strong authentication | JWT validation in APIM, role-aware admin API | Entra ID, APIM |
| Least privilege | Managed identity, scoped RBAC | Managed Identity, RBAC |
| Model governance | Per-team allow/deny config | Gateway policy engine |
| Request governance | Size checks, quotas, rate limits | APIM, gateway |
| Sensitive data detection | Regex and phrase inspection | Gateway policy engine |
| Auditability | Hash-based prompt logging, correlation IDs | App Insights, Log Analytics |
| Secrets protection | No hardcoded secrets, Key Vault only when needed | Key Vault |
| Network isolation | Private endpoints, VNET integration | Azure Networking |
| Change control | Versioned IaC and CI/CD | GitHub Actions/Azure DevOps |

## 9. API design
Gateway APIs:
- `GET /health`
- `POST /api/v1/chat`
- `POST /api/v1/embeddings`

Admin APIs:
- `GET /api/v1/admin/policies`
- `PUT /api/v1/admin/policies`
- `GET /api/v1/admin/quotas`
- `PUT /api/v1/admin/quotas`
- `GET /api/v1/admin/model-access`
- `PUT /api/v1/admin/model-access`
- `GET /api/v1/admin/blocked-requests`
- `GET /api/v1/admin/usage-summary`
- `GET /api/v1/admin/dashboard`

Identity headers for local MVP mode:
- `x-user-id`
- `x-app-id`
- `x-team`
- `x-roles`

## 10. APIM policy design with XML examples
Sample policy fragments are stored in [docs/apim-policy.xml](/Users/ersa3094/Documents/compliance/gateway/docs/apim-policy.xml). They include:
- JWT validation with Entra ID issuer and audience
- Correlation ID generation
- Request size enforcement
- Per-subscription or team rate limiting
- Backend managed identity authentication
- Diagnostic header propagation

## 11. Python project folder structure
```text
app/
  api/routes/
  core/
  logging/
  models/
  policies/
  services/
config/
docs/
infra/bicep/
pipelines/
tests/
artifacts/postman/
```

## 12. Complete sample code files
Core implementation files:
- [app/main.py](/Users/ersa3094/Documents/compliance/gateway/app/main.py)
- [ui.py](/Users/ersa3094/Documents/compliance/gateway/ui.py)
- [app/core/config.py](/Users/ersa3094/Documents/compliance/gateway/app/core/config.py)
- [app/core/auth.py](/Users/ersa3094/Documents/compliance/gateway/app/core/auth.py)
- [app/policies/policy_engine.py](/Users/ersa3094/Documents/compliance/gateway/app/policies/policy_engine.py)
- [app/policies/pii_detector.py](/Users/ersa3094/Documents/compliance/gateway/app/policies/pii_detector.py)
- [app/policies/injection_detector.py](/Users/ersa3094/Documents/compliance/gateway/app/policies/injection_detector.py)
- [app/logging/audit_logger.py](/Users/ersa3094/Documents/compliance/gateway/app/logging/audit_logger.py)
- [app/api/routes/gateway.py](/Users/ersa3094/Documents/compliance/gateway/app/api/routes/gateway.py)
- [app/api/routes/admin.py](/Users/ersa3094/Documents/compliance/gateway/app/api/routes/admin.py)
- [app/api/routes/health.py](/Users/ersa3094/Documents/compliance/gateway/app/api/routes/health.py)

## 13. Infrastructure as Code structure
Infrastructure code lives under [infra/bicep](/Users/ersa3094/Documents/compliance/gateway/infra/bicep) and is parameterized for environment, location, naming, and Azure resource references. Modules separate logging, identity, APIM, Key Vault, and application hosting concerns.

## 14. Example Bicep or Terraform files
This repository uses Bicep:
- [infra/bicep/main.bicep](/Users/ersa3094/Documents/compliance/gateway/infra/bicep/main.bicep)
- [infra/bicep/main.parameters.dev.json](/Users/ersa3094/Documents/compliance/gateway/infra/bicep/main.parameters.dev.json)
- [infra/bicep/modules/logging.bicep](/Users/ersa3094/Documents/compliance/gateway/infra/bicep/modules/logging.bicep)
- [infra/bicep/modules/identity.bicep](/Users/ersa3094/Documents/compliance/gateway/infra/bicep/modules/identity.bicep)
- [infra/bicep/modules/apim.bicep](/Users/ersa3094/Documents/compliance/gateway/infra/bicep/modules/apim.bicep)
- [infra/bicep/modules/app.bicep](/Users/ersa3094/Documents/compliance/gateway/infra/bicep/modules/app.bicep)
- [infra/bicep/modules/ui.bicep](/Users/ersa3094/Documents/compliance/gateway/infra/bicep/modules/ui.bicep)

## 15. CI/CD pipeline design
Stages:
1. Lint Python and validate formatting.
2. Run pytest unit tests.
3. Run lightweight SAST and dependency review.
4. Validate Bicep templates.
5. Build and publish the application artifact or image.
6. Deploy infra and app to target environment.
7. Execute smoke tests against `/health` and a controlled `/chat` call.

## 16. Example GitHub Actions or Azure DevOps pipeline YAML
Included:
- [/.github/workflows/ci.yml](/Users/ersa3094/Documents/compliance/gateway/.github/workflows/ci.yml)
- [pipelines/azure-devops.yml](/Users/ersa3094/Documents/compliance/gateway/pipelines/azure-devops.yml)

## 17. Logging schema
Audit events store:
- `timestamp`
- `user_id`
- `app_id`
- `team`
- `model`
- `deployment_name`
- `prompt_hash`
- `decision`
- `rule_hits`
- `estimated_tokens`
- `latency_ms`
- `response_status`
- `correlation_id`
- `action`
- `route`
- `warning_count`

Raw sensitive prompt text is not stored by default.

## 18. Monitoring dashboards and alert ideas
- Blocked request trend by team, model, and app.
- Warning-only prompt events by rule family.
- Quota exhaustion by team and user.
- Latency percentile for gateway and backend.
- Top models by request count and estimated tokens.
- Alert when blocked requests spike above baseline.
- Alert when APIM 401 or 429 rates exceed thresholds.
- Alert when gateway availability drops below SLA.

## 19. STRIDE threat model
See [docs/threat-model.md](/Users/ersa3094/Documents/compliance/gateway/docs/threat-model.md) for a fuller breakdown. Primary risks include token spoofing, prompt injection, quota abuse, model misuse, audit tampering, and data exfiltration through prompts or responses.

## 20. ISO 27001 control mapping
See [docs/iso27001-mapping.md](/Users/ersa3094/Documents/compliance/gateway/docs/iso27001-mapping.md). The MVP emphasizes access control, logging, secure configuration, change management, supplier/cloud governance, and incident response evidence.

## 21. .env.example
Environment variables are provided in [.env.example](/Users/ersa3094/Documents/compliance/gateway/.env.example).

## 22. Step-by-step deployment guide
Deployment guidance is in [docs/deployment-guide.md](/Users/ersa3094/Documents/compliance/gateway/docs/deployment-guide.md). It covers prerequisites, infra deployment, APIM policy import, app configuration, smoke testing, and manual steps.

## 23. Local development guide
Local development guidance is in [docs/local-development.md](/Users/ersa3094/Documents/compliance/gateway/docs/local-development.md).

## 24. Demo script for presenting to a CISO
The scripted walkthrough is in [docs/demo-script.md](/Users/ersa3094/Documents/compliance/gateway/docs/demo-script.md).

## 25. Backlog for phase 2 improvements
- Replace in-memory quota tracking with Redis or Cosmos DB.
- Add full OIDC token validation and JWK rotation in-app for zero-trust internal hops.
- Integrate Azure AI Content Safety Prompt Shields.
- Add Purview classification lookups and Defender posture checks.
- Introduce approval workflow for policy changes.
- Add signed audit export and immutable retention.
- Add chargeback reporting by business unit and environment.
- Support streaming completions and realtime policy hooks.

## Running the MVP
```bash
python3 -m pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8080
```

## Running the UI
```bash
streamlit run ui.py --server.port 8501
```

## Container build
```bash
docker build -t ozkan-gateway:local .
docker run --rm -p 8080:8080 --env-file .env ozkan-gateway:local

docker build -f Dockerfile.ui -t ozkan-gateway-ui:local .
docker run --rm -p 8501:8501 --env-file .env ozkan-gateway-ui:local
```

## Example curl commands
```bash
curl -s http://localhost:8080/health

curl -s http://localhost:8080/api/v1/chat \
  -H 'content-type: application/json' \
  -H 'x-user-id: analyst@contoso.com' \
  -H 'x-app-id: fin-assistant' \
  -H 'x-team: finance' \
  -d '{
    "model":"gpt-4o",
    "deployment_name":"gpt-4o-prod",
    "messages":[{"role":"user","content":"Summarize Q4 control remediation status."}]
  }'
```
# Activate the virtual environment
 
source venv/bin/activate

# # ##. #
- calisiyor

 ## # #  
 - next 

 Phase 1 — Harden the local MVP (days, not weeks)
Replace header-based auth with real JWT validation

Right now x-user-id, x-roles etc. are trusted headers — anyone can spoof them. Wire up Microsoft Entra ID:

# app/core/auth.py — replace parse_identity_header with real JWT validation
from jose import jwt, JWTError
import httpx

def get_jwks(tenant_id: str) -> dict:
    url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
    return httpx.get(url).json()

def verify_token(token: str, settings: Settings) -> IdentityContext:
    keys = get_jwks(settings.entra_tenant_id)
    claims = jwt.decode(token, keys, audience=settings.entra_audience)
    return IdentityContext(
        user_id=claims["upn"],
        app_id=claims.get("appid", ""),
        team=claims.get("extension_team", "default"),
        roles=claims.get("roles", []),
    )
Set REQUIRE_AUTH=true in .env once this is wired.

Persist quota state — current in-memory deques reset on restart. Drop in Redis:

# pip install redis
import redis
r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def check_and_consume(self, team, user_id):
    key = f"quota:{team}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    count = r.incr(key)
    r.expire(key, 90)  # 90s TTL covers the minute window
    ...
Switch audit log from flat file to structured sink — the JSONL file works locally but won't scale. Point it at Application Insights or a Log Analytics workspace:

from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

logger = logging.getLogger("audit")
logger.addHandler(AzureLogHandler(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
))
Phase 2 — Azure deployment (1–2 sprints)
The infra Bicep is already there. The deployment path:

Local dev
  └─► Docker build (Dockerfile + Dockerfile.ui)
        └─► Azure Container Registry (registry.bicep)
              └─► Azure Container Apps (app.bicep + ui.bicep)
                    └─► behind Azure API Management (apim.bicep)
                          └─► Entra ID app registration for auth
Key steps in order:

az login then az deployment sub create -f infra/bicep/main.bicep -p infra/bicep/main.parameters.dev.json
Push images to ACR — the azure-devops.yml pipeline already has the stages
Set ENABLE_LIVE_BACKEND=true and point OPENAI_BACKEND_URL at your real Azure OpenAI endpoint
Assign the Container App's managed identity the Cognitive Services OpenAI User role — no API keys needed
APIM sits in front of everything. The 
apim-policy.xml
 already has the JWT validation policy fragment. Apply it to the gateway product in APIM and your backend never sees unauthenticated traffic.

Phase 3 — Production-grade additions (ongoing)
Gap	Fix
PII detection is regex-only	Add Azure AI Content Safety or Microsoft Presidio for ML-based PII
No rate limiting at edge	Enable APIM rate-limit-by-key policy (already stubbed in apim-policy.xml)
Streamlit UI has no auth	Add streamlit-authenticator or put the UI behind APIM/Entra App Proxy
Audit log has no alerting	Create Log Analytics alert rules — e.g. >10 blocks/5min triggers a Sentinel incident
No secret rotation	Move OPENAI_API_KEY to Key Vault, reference via managed identity
Single region	Add a second Container Apps environment + APIM multi-region for HA
Quickest real-world win right now
Your .env already has real Azure credentials (AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT). Set:

ENABLE_LIVE_BACKEND=true
OPENAI_BACKEND_URL=https://ai-sal-test.cognitiveservices.azure.com/
OPENAI_API_KEY=<your key>
Then hit the Chat Tester — you'll get real GPT responses flowing through the policy engine, with audit events recorded. That's a working CISO demo in under 5 minutes.

The architecture is solid. The main gaps between MVP and production are auth hardening, persistent state, and getting it behind APIM in Azure — all of which your existing Bicep and pipeline already scaffold.