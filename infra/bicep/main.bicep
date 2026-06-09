targetScope = 'resourceGroup'

@description('Environment name')
param environment string = 'dev'

@description('Azure location')
param location string = resourceGroup().location

@description('Base name for resources')
param namePrefix string = 'ozkan'

@description('Container image reference for the gateway')
param containerImage string = 'replace-me.azurecr.io/ozkan-gateway:latest'

@description('Deploy the Streamlit governance UI')
param deployUi bool = false

@description('Container image reference for the Streamlit UI')
param uiImage string = 'replace-me.azurecr.io/ozkan-gateway-ui:latest'

@description('Azure OpenAI account name in the same resource group')
param azureOpenAiAccountName string

module logging './modules/logging.bicep' = {
  name: 'logging'
  params: {
    location: location
    namePrefix: namePrefix
    environment: environment
  }
}

module identity './modules/identity.bicep' = {
  name: 'identity'
  params: {
    location: location
    namePrefix: namePrefix
    environment: environment
  }
}

module registry './modules/registry.bicep' = {
  name: 'registry'
  params: {
    location: location
    namePrefix: namePrefix
    environment: environment
  }
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: registry.outputs.registryName
}

module apim './modules/apim.bicep' = {
  name: 'apim'
  params: {
    location: location
    namePrefix: namePrefix
    environment: environment
    appInsightsInstrumentationKey: logging.outputs.instrumentationKey
  }
}

module app './modules/app.bicep' = {
  name: 'app'
  params: {
    location: location
    namePrefix: namePrefix
    environment: environment
    containerImage: containerImage
    logAnalyticsWorkspaceCustomerId: logging.outputs.workspaceCustomerId
    logAnalyticsWorkspaceSharedKey: logging.outputs.workspaceSharedKey
    userAssignedIdentityId: identity.outputs.identityId
    registryServer: registry.outputs.loginServer
  }
}

module ui './modules/ui.bicep' = if (deployUi) {
  name: 'ui'
  params: {
    location: location
    namePrefix: namePrefix
    environment: environment
    uiImage: uiImage
    managedEnvironmentId: app.outputs.managedEnvironmentId
    registryServer: registry.outputs.loginServer
    userAssignedIdentityId: identity.outputs.identityId
    backendBaseUrl: app.outputs.applicationUrl
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${namePrefix}-${environment}-kv'
  location: location
  properties: {
    enableRbacAuthorization: true
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    publicNetworkAccess: 'Disabled'
  }
}

resource openAiAccount 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: azureOpenAiAccountName
}

resource openAiRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(openAiAccount.id, identity.outputs.principalId, 'openai-user-role')
  scope: openAiAccount
  properties: {
    principalId: identity.outputs.principalId
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a001fd3d-188f-4b5d-821b-7da978bf7442'
    )
    principalType: 'ServicePrincipal'
  }
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.outputs.registryId, identity.outputs.principalId, 'acr-pull-role')
  scope: containerRegistry
  properties: {
    principalId: identity.outputs.principalId
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7f951dda-4ed3-4680-a7ca-43fe172d538d'
    )
    principalType: 'ServicePrincipal'
  }
}

output apiManagementName string = apim.outputs.apimName
output applicationUrl string = app.outputs.applicationUrl
output keyVaultName string = keyVault.name
output containerRegistryLoginServer string = registry.outputs.loginServer
output uiUrl string = deployUi ? ui.outputs.uiUrl : 'ui-not-deployed'
