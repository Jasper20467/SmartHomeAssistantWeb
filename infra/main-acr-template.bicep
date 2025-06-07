@description('應用程式名稱')
param appName string = 'jyhomeapp'

@description('資源部署的位置')
param location string = resourceGroup().location

@description('容器映像版本')
param imageVersion string = '1.0'

@description('PostgreSQL 資料庫密碼')
@secure()
param dbPassword string

@description('Azure Container Registry 名稱')
param acrName string

@description('Azure Container Registry 密碼')
@secure()
param acrPassword string

// 建立 Log Analytics 工作區以供監控
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: '${toLower(appName)}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// 建立 Container Apps 環境
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2022-06-01-preview' = {
  name: '${toLower(appName)}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

// 建立 Container App - 資料庫
resource dbApp 'Microsoft.App/containerApps@2022-06-01-preview' = {
  name: '${toLower(appName)}-db'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: false
        targetPort: 5432
        transport: 'http'
        allowInsecure: true
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: []
      secrets: [
        {
          name: 'db-password'
          value: dbPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'db'
          image: 'postgres:14'
          env: [
            {
              name: 'POSTGRES_DB'
              value: 'smarthome'
            }
            {
              name: 'POSTGRES_USER'
              value: 'postgres'
            }
            {
              name: 'POSTGRES_PASSWORD'
              secretRef: 'db-password'
            }
          ]
          volumeMounts: [
            {
              mountPath: '/var/lib/postgresql/data'
              volumeName: 'postgres-data'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
      volumes: [
        {
          name: 'postgres-data'
          storageType: 'EmptyDir'
        }
      ]
    }
  }
}

// 建立 Container App - 後端
resource backendApp 'Microsoft.App/containerApps@2022-06-01-preview' = {
  name: '${toLower(appName)}-backend'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acrName
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'db-password'
          value: dbPassword
        }
        {
          name: 'acr-password'
          value: acrPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: '${acrName}.azurecr.io/smarthomeassistantweb-backend:${imageVersion}'
          env: [
            {
              name: 'DATABASE_URL'
              value: 'postgresql://postgres:${dbPassword}@${dbApp.name}.${containerAppsEnvironment.properties.defaultDomain}:5432/smarthome'
            }
            {
              name: 'DATABASE_HOST'
              value: '${dbApp.name}.${containerAppsEnvironment.properties.defaultDomain}'
            }
            {
              name: 'DATABASE_PORT'
              value: '5432'
            }
            {
              name: 'DATABASE_NAME'
              value: 'smarthome'
            }
            {
              name: 'DATABASE_USER'
              value: 'postgres'
            }
            {
              name: 'DATABASE_PASSWORD'
              secretRef: 'db-password'
            }
          ]
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

// 建立 Container App - 前端
resource frontendApp 'Microsoft.App/containerApps@2022-06-01-preview' = {
  name: '${toLower(appName)}-frontend'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 80
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acrName
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acrPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: '${acrName}.azurecr.io/smarthomeassistantweb-frontend:${imageVersion}'
          env: [
            {
              name: 'NODE_ENV'
              value: 'production'
            }
            {
              name: 'API_URL'
              value: 'https://${backendApp.properties.configuration.ingress.fqdn}'
            }
          ]
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

output frontendUrl string = 'https://${frontendApp.properties.configuration.ingress.fqdn}'
output backendUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'
