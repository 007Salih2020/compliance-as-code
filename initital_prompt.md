You are a Principal Azure Cloud Architect, DevSecOps Engineer, AI Security Architect, Python Engineer, and ISO 27001-aware compliance designer.

Design and generate a production-style MVP project called:

Enterprise AI Security Gateway for Azure OpenAI / Azure AI Foundry

## Mission
Build a centralized, enterprise-grade AI Security Gateway that sits in front of Azure OpenAI / Azure AI Foundry and enforces security, compliance, observability, and cost governance for all internal LLM traffic.

The project must be realistic, deployable, and persuasive to a Chief Information Security Officer.

## Business context
Today, multiple internal teams call Azure OpenAI directly using keys with inconsistent security controls, weak observability, and no centralized governance.

We need a single governed entry point that:
- authenticates users and apps with Microsoft Entra ID
- sends all LLM traffic through Azure API Management
- authenticates APIM to Azure OpenAI / Foundry using managed identity where possible
- enforces model access policies, quotas, and rate limits
- inspects prompts and responses for security/compliance risks
- creates compliance-friendly audit logs and dashboards
- provides an admin API/UI for governance operations
- can be extended later with Microsoft security and compliance services

## Technical goals
Generate a complete starter project with:
- README.md
- architecture overview
- threat model
- implementation plan
- Python application code
- Infrastructure as Code
- CI/CD pipeline
- sample configuration
- .env.example
- test stubs
- sample APIM policy fragments
- deployment instructions
- demo walkthrough for security leadership

## Required architecture
Use these Azure components:
- Azure API Management as the mandatory front door
- Azure OpenAI or Azure AI Foundry model deployments as backend
- Microsoft Entra ID for client authentication and authorization
- Managed Identity from APIM and app services to Azure resources whenever possible
- Azure Key Vault for secrets only where absolutely necessary
- Log Analytics and Application Insights for telemetry
- Optional hooks for Microsoft Defender for Cloud, Microsoft Purview, and Azure AI Content Safety Prompt Shields

## MVP capabilities
Implement the following MVP scope:

1. Gateway enforcement
- APIM receives all requests for /chat, /embeddings, and /admin APIs
- JWT validation using Entra ID
- model allowlist and denylist by team/app/environment
- per-user and per-team quotas
- rate limiting
- request size validation
- correlation IDs for tracing

2. Prompt inspection
Create Python logic that inspects requests before they are forwarded.
Detect and score:
- email addresses
- credit card-like patterns
- secrets or credentials
- jailbreak phrases
- prompt injection phrases such as “ignore previous instructions”
- forbidden internal project code names from a configurable list

For MVP use deterministic rules with regex/string matching.
Return a policy decision:
- allow
- allow_with_warning
- block

3. Response inspection
Add a lightweight response validation/redaction layer for:
- obvious secrets
- accidental PII echo
- policy violation indicators

4. Audit logging
Log every decision with:
- timestamp
- user ID
- app ID
- team
- model
- deployment name
- prompt hash
- decision
- rule hits
- estimated tokens
- latency
- response status
- correlation ID

Do not store raw sensitive prompt content in logs by default.
Store masked or hashed values when possible.

5. Admin service
Build a Python FastAPI service with:
- health endpoint
- policy management endpoints
- team quota management
- model access policy management
- blocked request listing
- usage summary endpoint
- simple HTML admin page or JSON-first API

6. Developer experience
Project must include:
- Makefile or task runner
- local run instructions
- pytest tests
- linting configuration
- example curl commands
- sample Postman collection or equivalent examples

## Security and compliance requirements
Design with security-first defaults:
- HTTPS only
- least privilege
- managed identities preferred over static secrets
- no hardcoded credentials
- private endpoints and VNET integration described in architecture
- role separation for platform admin, security admin, and app teams
- audit-friendly logging
- mapping to ISO 27001 style controls such as access control, logging, change management, secure configuration, and supplier/cloud governance

## Deliverables to generate
Generate the output in this exact order:

1. Executive summary
2. Why this project matters to a CISO
3. MVP scope and non-goals
4. Target architecture
5. Architecture diagram description in text
6. Trust boundaries and data flows
7. Azure resource inventory
8. Security control matrix
9. API design
10. APIM policy design with XML examples
11. Python project folder structure
12. Complete sample code files
13. Infrastructure as Code structure
14. Example Bicep or Terraform files
15. CI/CD pipeline design
16. Example GitHub Actions or Azure DevOps pipeline YAML
17. Logging schema
18. Monitoring dashboards and alert ideas
19. STRIDE threat model
20. ISO 27001 control mapping
21. .env.example
22. Step-by-step deployment guide
23. Local development guide
24. Demo script for presenting to a CISO
25. Backlog for phase 2 improvements

## Code requirements
Use Python 3.11+.
Prefer:
- FastAPI
- pydantic
- httpx
- uvicorn
- pytest

Structure the code cleanly, with:
- app/api
- app/core
- app/models
- app/services
- app/policies
- app/logging
- infra
- pipelines
- docs
- tests

Generate:
- main.py
- config.py
- auth.py
- policy_engine.py
- pii_detector.py
- injection_detector.py
- audit_logger.py
- routes for admin and health
- sample model routing config
- sample policy config YAML or JSON

## Infrastructure as Code requirements
Provide either Bicep or Terraform.
Include:
- APIM
- Log Analytics
- Application Insights
- Key Vault
- Managed Identity
- Container Apps or App Service for admin API
- Azure OpenAI / Foundry references
- role assignments
- environment parameterization for dev/test/prod

## CI/CD requirements
Include pipeline stages for:
- lint
- unit test
- SAST/dependency checks
- IaC validation
- deployment
- smoke tests

## Output quality bar
Be concrete, implementation-ready, and opinionated.
Do not stay high-level.
Write the README.md in a professional enterprise style.
Generate working starter code, not pseudocode, unless a cloud-specific resource must be stubbed.
Where something cannot be fully automated, clearly mark it as manual and explain why.

## Final requirement
At the end, output the final repository tree and a “Day 1 demo scenario” that shows:
- one valid request
- one blocked prompt injection request
- one PII-containing request
- one quota-exceeded request
- the corresponding audit log entries and dashboard outcomes