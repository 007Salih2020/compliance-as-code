param location string
param namePrefix string
param environment string
param appInsightsInstrumentationKey string

resource apim 'Microsoft.ApiManagement/service@2023-05-01-preview' = {
  name: '${namePrefix}-${environment}-apim'
  location: location
  sku: {
    name: 'Developer'
    capacity: 1
  }
  properties: {
    publisherEmail: 'platform@contoso.com'
    publisherName: 'Contoso Platform Security'
    virtualNetworkType: 'None'
    customProperties: {
      'ApplicationInsights.InstrumentationKey': appInsightsInstrumentationKey
    }
  }
}

output apimName string = apim.name
