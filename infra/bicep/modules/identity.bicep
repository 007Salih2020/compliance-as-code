param location string
param namePrefix string
param environment string

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${namePrefix}-${environment}-id'
  location: location
}

output identityId string = identity.id
output principalId string = identity.properties.principalId
