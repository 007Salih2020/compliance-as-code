# CISO Demo Script

## Storyline
Show that enterprise AI usage is no longer a direct uncontrolled call to Azure OpenAI. Every request now passes through a governed gateway with identity, policy, logging, and quota controls.

## Sequence
1. Open the architecture overview and explain the APIM-first trust boundary.
2. Show the config files for team model access and quotas.
3. Run a valid request and show the success path plus audit event.
4. Run a prompt injection request and show the immediate block with rule hits.
5. Run a PII-bearing request and show `allow_with_warning`.
6. Run repeated requests until quota exhaustion and show the `429` plus usage summary.
7. Open `/api/v1/admin/dashboard` and explain blocked trend, tokens by team, and correlation IDs.
