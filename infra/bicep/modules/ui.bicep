param location string
param namePrefix string
param environment string
param uiImage string
param managedEnvironmentId string
param registryServer string
param userAssignedIdentityId string
param backendBaseUrl string

resource uiApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-${environment}-ui'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    configuration: {
      registries: [
        {
          server: registryServer
          identity: userAssignedIdentityId
        }
      ]
      ingress: {
        external: true
        targetPort: 8501
      }
    }
    template: {
      containers: [
        {
          name: 'ui'
          image: uiImage
          env: [
            {
              name: 'UI_BACKEND_URL'
              value: backendBaseUrl
            }
          ]
          resources: {
            cpu: 0.5
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 2
      }
    }
  }
}

output uiUrl string = 'https://${uiApp.properties.configuration.ingress.fqdn}'
