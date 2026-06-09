param location string
param namePrefix string
param environment string
param containerImage string
param logAnalyticsWorkspaceCustomerId string
param logAnalyticsWorkspaceSharedKey string
param userAssignedIdentityId string
param registryServer string

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${namePrefix}-${environment}-cae'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspaceCustomerId
        sharedKey: logAnalyticsWorkspaceSharedKey
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-${environment}-gateway'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnvironment.id
    configuration: {
      registries: [
        {
          server: registryServer
          identity: userAssignedIdentityId
        }
      ]
      ingress: {
        external: false
        targetPort: 8080
      }
    }
    template: {
      containers: [
        {
          name: 'gateway'
          image: containerImage
          resources: {
            cpu: 0.5
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output applicationUrl string = 'https://internal-only-via-apim'
output applicationFqdn string = app.properties.configuration.ingress.fqdn
output managedEnvironmentId string = managedEnvironment.id
