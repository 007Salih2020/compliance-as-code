# STRIDE Threat Model

## Spoofing
- Risk: Forged user or app identity reaches the backend.
- Mitigation: APIM validates JWTs against Entra ID, backend trusts only APIM ingress, admin APIs require elevated roles.

## Tampering
- Risk: Policy files or audit records are altered.
- Mitigation: Store config in version control, restrict write roles, send logs to centralized immutable retention, use deployment approvals.

## Repudiation
- Risk: Callers deny abusive or sensitive prompts.
- Mitigation: Correlation IDs, prompt hashing, team and app identifiers, centralized audit trail.

## Information Disclosure
- Risk: Sensitive data leaves through prompts, completions, or logs.
- Mitigation: Deterministic inspection, response redaction, no raw prompt storage by default, private networking.

## Denial of Service
- Risk: Excessive traffic overwhelms APIM or backend models.
- Mitigation: APIM rate limits, gateway quotas, request size checks, autoscaling and monitoring.

## Elevation of Privilege
- Risk: App team gains access to restricted models or admin functions.
- Mitigation: Team-specific model policies, RBAC, separate admin roles, managed identity to downstream resources.
