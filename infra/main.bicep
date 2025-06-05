@description('應用程式名稱')
param appName string = 'JYHomeAssistant'

@description('資源組名稱')
param resourceGroupName string = 'JYSmartHomeAssistant'

@description('Azure Container Registry名稱')
param acrName string = 'jasperbasicacr'

@description('資源部署的位置')
param location string = resourceGroup().location

@description('容器映像版本')
param imageVersion string = '1.0'

@description('PostgreSQL 資料庫密碼')
@secure()
param dbPassword string = 'YourSecurePassword123!' // 個人使用場景下的預設密碼，生產環境中請更改

@description('Azure Container Registry密碼')
@secure()
param acrPassword string = '' // 部署前請填寫您的ACR密碼

@description('環境變數')
param environmentName string = 'dev'

// 參考現有的 Azure Container Registry 
resource acr 'Microsoft.ContainerRegistry/registries@2021-12-01-preview' existing = {
  name: acrName
}

// 建立 Log Analytics 工作區以供監控
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: '${appName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018' // 按用量收費
    }
    retentionInDays: 30
  }
}

// 建立 Container Apps 環境
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2022-06-01-preview' = {
  name: '${appName}-env'
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

// 建立 Container App - 前端
resource frontendApp 'Microsoft.App/containerApps@2022-06-01-preview' = {
  name: '${appName}-frontend'
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
          server: acr.properties.loginServer
          username: acr.name
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
          image: '${acr.properties.loginServer}/smarthomeassistantweb-frontend:${imageVersion}'
          env: [
            {
              name: 'NODE_ENV'
              value: 'production'
            },
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
        maxReplicas: 1 // 個人使用不需要太多副本
      }
    }
  }
}

// 建立 Container App - 後端
resource backendApp 'Microsoft.App/containerApps@2022-06-01-preview' = {
  name: '${appName}-backend'
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
          server: acr.properties.loginServer
          username: acr.name
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acrPassword
        }
        {
          name: 'db-password'
          value: dbPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: '${acr.properties.loginServer}/smarthomeassistantweb-backend:${imageVersion}'
          env: [
            {
              name: 'DATABASE_URL'
              value: 'postgresql://postgres:${dbPassword}@${dbApp.properties.configuration.ingress.fqdn}:5432/smarthome'
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

// 建立 Container App - 資料庫
resource dbApp 'Microsoft.App/containerApps@2022-06-01-preview' = {
  name: '${appName}-db'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: false // 內部服務，不需要外部存取
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
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.name
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acrPassword
        }
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
          image: 'postgres:1.0'
          env: [
            {
              name: 'POSTGRES_DB'
              value: 'smarthome'
            }
            {
              name: 'POSTGRES_PASSWORD'
              secretRef: 'db-password'
            }
            {
              name: 'POSTGRES_USER'
              value: 'postgres'
            }
          ]
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
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

/* 
// 建立 Container App - LineBot (暫時註解掉，不部署LineBot)
resource linebotApp 'Microsoft.App/containerApps@2022-06-01-preview' = {
  name: '${appName}-linebot'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 5000
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
          server: acr.properties.loginServer
          username: acr.name
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
          name: 'linebot'
          image: '${acr.properties.loginServer}/smarthomeassistantweb-linebot:${imageVersion}'
          env: [
            {
              name: 'BACKEND_URL'
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
*/

output frontendUrl string = 'https://${frontendApp.properties.configuration.ingress.fqdn}'
output backendUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'
// output linebotUrl string = 'https://${linebotApp.properties.configuration.ingress.fqdn}'  // 暫時註解掉LineBot輸出