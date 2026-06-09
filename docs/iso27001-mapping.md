# ISO 27001 Style Control Mapping

| ISO 27001 Theme | MVP Implementation |
| --- | --- |
| Access control | Entra ID, APIM JWT validation, admin-role separation |
| Logging and monitoring | Audit logger, Application Insights, Log Analytics, alerts |
| Secure configuration | Bicep templates, environment parameterization, no hardcoded credentials |
| Change management | CI/CD pipelines, IaC review, policy-as-code files |
| Asset and supplier governance | Azure resource inventory, managed service dependency documentation |
| Operations security | Rate limits, quotas, request inspection, deployment guidance |
| Incident support | Correlation IDs, blocked request reports, dashboard metrics |
