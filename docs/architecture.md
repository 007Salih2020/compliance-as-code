# Architecture Overview

The gateway is designed around a mandatory APIM ingress that terminates client traffic, validates Microsoft Entra ID tokens, and forwards only normalized, correlated requests to the FastAPI control plane. The FastAPI service performs deterministic prompt and response inspection, team-based model authorization, and quota enforcement before proxying to Azure OpenAI or Azure AI Foundry.

Recommended production network posture:
- APIM in internal VNET mode or with private inbound controls.
- Gateway app deployed to Container Apps or App Service with VNET integration.
- Private Endpoints for Azure OpenAI, Key Vault, and monitoring destinations where supported.
- Managed identity from APIM and gateway to downstream Azure resources.

Separation of duties:
- Platform admin owns APIM, networking, hosting, and deployment pipelines.
- Security admin owns policy content, blocked phrases, code names, and monitoring rules.
- App teams consume gateway endpoints and request access to models through change control.
