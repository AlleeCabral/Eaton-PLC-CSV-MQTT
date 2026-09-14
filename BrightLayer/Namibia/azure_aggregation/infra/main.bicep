@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Storage account name')
param storageAccountName string

@description('Key Vault name')
param keyVaultName string

@description('Application Insights name')
param appInsightsName string

@description('Flex Consumption Function App name')
param functionAppName string

@description('Flex Consumption plan name')
param planName string

@description('Keep scheduling disabled until live configuration passes its gate')
param schedulerDisabled bool = true

param expectedPlcCount int = 15
param cycleIntervalMinutes int = 5
param cycleSchedule string = '0 */5 * * * *'
param cycleQueueName string = 'aggregation-cycles'
param cycleGraceSeconds int = 90
param fetchOverlapMinutes int = 15
param aggregationMode string = 'permissive'
@allowed([
  'dry_run'
  'enabled'
])
param writebackMode string = 'dry_run'
param lastKnownValuePolicy string = 'carry_forward'
param zeroFillDisabled bool = true
param plcStaleTimeoutSeconds int = 300
param plcOfflineTimeoutSeconds int = 600
param maxRetries int = 3
param retryBaseSeconds int = 10
param cycleTableStatus string = 'CycleStatus'
param cycleTableSnapshot string = 'CycleDataSnapshot'
param cycleTableAudit string = 'CycleAudit'
param cycleTableLatest string = 'LatestObservation'
param retentionHours int = 48

var storageConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
}

resource deploymentContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'function-packages'
  properties: {
    publicAccess: 'None'
  }
}

resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
}

resource cycleQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2023-05-01' = {
  parent: queueService
  name: cycleQueueName
}

resource tableService 'Microsoft.Storage/storageAccounts/tableServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
}

resource statusTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: cycleTableStatus
}

resource snapshotTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: cycleTableSnapshot
}

resource auditTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: cycleTableAudit
}

resource latestTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: cycleTableLatest
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource hostingPlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: planName
  location: location
  kind: 'functionapp'
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2024-04-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    httpsOnly: true
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: '${storageAccount.properties.primaryEndpoints.blob}${deploymentContainer.name}'
          authentication: {
            type: 'StorageAccountConnectionString'
            storageAccountConnectionStringName: 'DEPLOYMENT_STORAGE_CONNECTION_STRING'
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.11'
      }
      scaleAndConcurrency: {
        instanceMemoryMB: 2048
        maximumInstanceCount: 100
      }
    }
    siteConfig: {
      appSettings: [
        { name: 'AzureWebJobsStorage', value: storageConnectionString }
        { name: 'DEPLOYMENT_STORAGE_CONNECTION_STRING', value: storageConnectionString }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.properties.ConnectionString }
        { name: 'AzureWebJobs.cycle_planner_timer.Disabled', value: string(schedulerDisabled) }
        { name: 'EXPECTED_PLC_COUNT', value: string(expectedPlcCount) }
        { name: 'CYCLE_INTERVAL_MINUTES', value: string(cycleIntervalMinutes) }
        { name: 'CYCLE_SCHEDULE', value: cycleSchedule }
        { name: 'CYCLE_QUEUE_NAME', value: cycleQueueName }
        { name: 'CYCLE_GRACE_SECONDS', value: string(cycleGraceSeconds) }
        { name: 'FETCH_OVERLAP_MINUTES', value: string(fetchOverlapMinutes) }
        { name: 'AGGREGATION_MODE', value: aggregationMode }
        { name: 'WRITEBACK_MODE', value: writebackMode }
        { name: 'LAST_KNOWN_VALUE_POLICY', value: lastKnownValuePolicy }
        { name: 'ZERO_FILL_DISABLED', value: string(zeroFillDisabled) }
        { name: 'PLC_STALE_TIMEOUT_SECONDS', value: string(plcStaleTimeoutSeconds) }
        { name: 'PLC_OFFLINE_TIMEOUT_SECONDS', value: string(plcOfflineTimeoutSeconds) }
        { name: 'MAX_RETRIES', value: string(maxRetries) }
        { name: 'RETRY_BASE_SECONDS', value: string(retryBaseSeconds) }
        { name: 'CYCLE_TABLE_STATUS', value: cycleTableStatus }
        { name: 'CYCLE_TABLE_SNAPSHOT', value: cycleTableSnapshot }
        { name: 'CYCLE_TABLE_AUDIT', value: cycleTableAudit }
        { name: 'CYCLE_TABLE_LATEST', value: cycleTableLatest }
        { name: 'RETENTION_HOURS', value: string(retentionHours) }
        { name: 'KEYVAULT_URI', value: keyVault.properties.vaultUri }
      ]
    }
  }
}

resource keyVaultSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, functionApp.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
  }
}

output functionAppPrincipalId string = functionApp.identity.principalId
output functionAppName string = functionApp.name
output storageAccountId string = storageAccount.id
output keyVaultId string = keyVault.id
output cycleQueueName string = cycleQueue.name
