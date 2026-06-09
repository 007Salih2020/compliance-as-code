# Deployment Guide

## Prerequisites
- Azure subscription with permissions for APIM, networking, managed identity, and application hosting.
- Azure OpenAI or Azure AI Foundry account and model deployments already approved.
- Azure CLI, Bicep CLI, and either GitHub Actions or Azure DevOps service connections.

## Steps
1. Create or select a resource group per environment.
2. Deploy Bicep:
   `az deployment group create --resource-group <rg> --template-file infra/bicep/main.bicep --parameters @infra/bicep/main.parameters.dev.json`
3. Build the API container image locally:
   `docker build -t ozkan-gateway:local .`
4. Build the UI container image locally:
   `docker build -f Dockerfile.ui -t ozkan-gateway-ui:local .`
5. Push the images to Azure Container Registry:
   `az acr build --registry <acr-name> --image ozkan-gateway:latest .`
   `az acr build --registry <acr-name> --image ozkan-gateway-ui:latest -f Dockerfile.ui .`
6. Update the deployment parameters:
   - `containerImage=<acr-login-server>/ozkan-gateway:latest`
   - `uiImage=<acr-login-server>/ozkan-gateway-ui:latest`
   - `deployUi=true` when you want the governance console deployed
7. Configure app settings from `.env.example`, replacing placeholders with environment values.
8. Assign managed identity roles:
   - Gateway to Azure OpenAI `Cognitive Services OpenAI User`
   - Gateway to Key Vault `Key Vault Secrets User` only if required
   - APIM to backend according to the chosen auth pattern
9. Import [docs/apim-policy.xml](/Users/ersa3094/Documents/compliance/gateway/docs/apim-policy.xml) into APIM APIs and products.
10. Enable APIM diagnostics to Log Analytics and Application Insights.
11. Run smoke tests:
   - `GET /health`
   - Valid `/chat`
   - Blocked `/chat`
   - Admin usage summary

## Manual steps
- Entra application registration and audience selection.
- Private DNS setup for private endpoints.
- APIM custom domain and certificate binding.
- Production alert routing and retention policies.
