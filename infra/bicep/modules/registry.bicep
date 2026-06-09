param location string
param namePrefix string
param environment string

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: toLower('${namePrefix}${environment}acr')
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

output registryId string = registry.id
output registryName string = registry.name
output loginServer string = registry.properties.loginServer
