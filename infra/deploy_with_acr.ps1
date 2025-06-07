param (
    [string]$resourceGroupName = "JYSmartHomeAssistant",
    [string]$location = "eastasia",
    [string]$appName = "jyhomeassistant",
    [string]$dbPassword = "YourSecurePassword123!",
    [string]$imageTag = "1.0",
    [string]$acrName = "",
    [string]$acrPassword = ""
)

# 顯示歡迎訊息
Write-Host "====== jyhomeassistant 部署腳本 (Container Apps 版 - ACR) ======" -ForegroundColor Green
Write-Host "此腳本將幫助您將 jyhomeassistant 部署到 Azure Container Apps" -ForegroundColor Green
Write-Host "使用 Azure Container Registry (ACR) 映像" -ForegroundColor Cyan
Write-Host ""

# 參數驗證
if ([string]::IsNullOrEmpty($acrName)) {
    Write-Host "錯誤：需要提供 ACR 名稱。使用 -acrName 參數指定 ACR 名稱。" -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrEmpty($acrPassword)) {
    Write-Host "錯誤：需要提供 ACR 密碼。使用 -acrPassword 參數指定 ACR 密碼。" -ForegroundColor Red
    exit 1
}

# 登入 Azure
Write-Host "正在登入 Azure..." -ForegroundColor Yellow
az login
if ($LASTEXITCODE -ne 0) {
    Write-Host "Azure 登入失敗，腳本終止。" -ForegroundColor Red
    exit 1
}

# 確認資源群組存在，若不存在則建立
Write-Host "檢查資源群組 $resourceGroupName 是否存在..." -ForegroundColor Yellow
$rgExists = az group exists --name $resourceGroupName
if ($rgExists -eq "false") {
    Write-Host "資源群組不存在，正在建立..." -ForegroundColor Yellow
    az group create --name $resourceGroupName --location $location
    if ($LASTEXITCODE -ne 0) {
        Write-Host "資源群組建立失敗，腳本終止。" -ForegroundColor Red
        exit 1
    }
    Write-Host "資源群組建立成功。" -ForegroundColor Green
} else {
    Write-Host "資源群組已存在。" -ForegroundColor Green
}

# 檢查 ACR 存在性
Write-Host "檢查 Azure Container Registry $acrName 是否存在..." -ForegroundColor Yellow
$acrExists = az acr check-name --name $acrName --query "nameAvailable" -o tsv
if ($acrExists -eq "true") {
    Write-Host "ACR $acrName 不存在，請檢查名稱是否正確或創建新的 ACR。" -ForegroundColor Red
    $createAcr = Read-Host "是否立即創建新的 ACR? (Y/N)"
    if ($createAcr -eq "Y" -or $createAcr -eq "y") {
        Write-Host "正在創建 ACR $acrName..." -ForegroundColor Yellow
        az acr create --resource-group $resourceGroupName --name $acrName --sku Basic
        Write-Host "ACR 創建完成，請確保您已準備好 ACR 密碼。" -ForegroundColor Green
    } else {
        Write-Host "操作取消，請提供有效的 ACR 名稱和密碼。" -ForegroundColor Red
        exit 1
    }
}

# 檢查資料庫密碼是否為預設值，若是則詢問是否更改
if ($dbPassword -eq "YourSecurePassword123!") {
    Write-Host "檢測到默認資料庫密碼，建議更改為更安全的密碼。" -ForegroundColor Yellow
    $changePassword = Read-Host "是否更改資料庫密碼? (Y/N)"
    if ($changePassword -eq "Y" -or $changePassword -eq "y") {
        Write-Host "請輸入新的資料庫密碼(輸入將被隱藏):" -ForegroundColor Yellow
        $securePassword = Read-Host -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        $dbPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    }
}

# 確認 Azure CLI 擴充功能
Write-Host "檢查並安裝所需的 Azure CLI 擴充功能..." -ForegroundColor Yellow
$extensions = @("containerapp")
foreach ($extension in $extensions) {
    $installed = az extension list --query "[?name=='$extension'].name" -o tsv
    if (-not $installed) {
        Write-Host "安裝 $extension 擴充功能..." -ForegroundColor Yellow
        az extension add --name $extension
    }
}

# 檢查 Container Apps 提供者註冊
Write-Host "確保 Container Apps 資源提供者已註冊..." -ForegroundColor Yellow
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

# 創建暫時性 Bicep 文件
Write-Host "正在修改 Bicep 文件以使用 ACR..." -ForegroundColor Yellow
$mainBicepContent = Get-Content -Path ./main.bicep -Raw

# 讀取原始 Bicep 文件來檢查其是否已經支持 ACR
if ($mainBicepContent -notmatch "param acrName string") {
    # 如果文件中沒有 ACR 參數，需要複製並修改
    $backupFile = "./main.bicep.backup"
    Copy-Item -Path ./main.bicep -Destination $backupFile -Force
    Write-Host "原始 Bicep 文件已備份為 $backupFile" -ForegroundColor Yellow
    
    # 創建新的 ACR 參數定義
    $acrParams = @"

@description('Azure Container Registry 名稱')
param acrName string

@description('Azure Container Registry 密碼')
@secure()
param acrPassword string
"@
    
    # 插入參數到文件開頭的適當位置
    $mainBicepContent = $mainBicepContent -replace "(@description\('環境變數'\)\r?\nparam environmentName string = 'dev')", "$acrParams`r`n`r`n`$1"
    
    # 修改每個容器應用的配置，從 Docker Hub 換成 ACR
    # 修改前端配置
    $mainBicepContent = $mainBicepContent -replace "// 使用 Docker Hub，不需要認證\r?\n      registries: \[\]", @"
// 使用 Azure Container Registry
      registries: [
        {
          server: '$`{acrName}.azurecr.io'
          username: acrName
          passwordSecretRef: 'acr-password'
        }
      ]
"@
    
    # 添加 ACR 密碼 secret
    $mainBicepContent = $mainBicepContent -replace "secrets: \[\]", @"
secrets: [
        {
          name: 'acr-password'
          value: acrPassword
        }
      ]
"@
    
    # 修改後端配置，添加 ACR 認證
    $mainBicepContent = $mainBicepContent -replace "// 使用 Docker Hub，不需要 ACR 認證\r?\n      registries: \[\]", @"
// 使用 Azure Container Registry
      registries: [
        {
          server: '$`{acrName}.azurecr.io'
          username: acrName
          passwordSecretRef: 'acr-password'
        }
      ]
"@
    
    # 修改映像路徑
    $mainBicepContent = $mainBicepContent -replace "image: 'popo510691/homeassistant\.frontend:\$\{imageVersion\}'", "image: '$`{acrName}.azurecr.io/smarthomeassistantweb-frontend:$`{imageVersion}'"
    $mainBicepContent = $mainBicepContent -replace "image: 'popo510691/homeassistant\.backend:\$\{imageVersion\}'", "image: '$`{acrName}.azurecr.io/smarthomeassistantweb-backend:$`{imageVersion}'"
    
    # 寫入修改後的文件到臨時文件
    $tempBicepFile = "./main-acr.bicep"
    Set-Content -Path $tempBicepFile -Value $mainBicepContent
    Write-Host "已創建修改後的 Bicep 文件: $tempBicepFile" -ForegroundColor Green
} else {
    # 如果文件已支持 ACR，直接使用原文件
    Write-Host "Bicep 文件已支持 ACR，將直接使用。" -ForegroundColor Green
    $tempBicepFile = "./main.bicep"
}

# 預覽部署
Write-Host "預覽 Bicep 部署..." -ForegroundColor Yellow
az deployment group what-if `
    --resource-group $resourceGroupName `
    --template-file $tempBicepFile `
    --parameters appName=$appName `
    --parameters dbPassword=$dbPassword `
    --parameters imageVersion=$imageTag `
    --parameters acrName=$acrName `
    --parameters acrPassword=$acrPassword

$confirm = Read-Host "是否繼續部署? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "已取消部署。" -ForegroundColor Yellow
    exit 0
}

# 部署 Bicep 模板
Write-Host "開始部署 Bicep 模板..." -ForegroundColor Yellow
$deploymentOutput = az deployment group create `
    --resource-group $resourceGroupName `
    --template-file $tempBicepFile `
    --parameters appName=$appName `
    --parameters dbPassword=$dbPassword `
    --parameters imageVersion=$imageTag `
    --parameters acrName=$acrName `
    --parameters acrPassword=$acrPassword `
    --query "properties.outputs" -o json

if ($LASTEXITCODE -ne 0) {
    Write-Host "部署失敗，請檢查錯誤訊息。" -ForegroundColor Red
    exit 1
}

# 解析部署輸出
$outputs = $deploymentOutput | ConvertFrom-Json
$frontendUrl = $outputs.frontendUrl.value
$backendUrl = $outputs.backendUrl.value

# 輸出部署結果
Write-Host "部署成功完成！" -ForegroundColor Green
Write-Host "===================== 應用程式網址 =====================" -ForegroundColor Cyan
Write-Host "前端應用: $frontendUrl" -ForegroundColor White
Write-Host "後端API: $backendUrl" -ForegroundColor White
Write-Host "註: LineBot 服務暫時未部署" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "提示：如果您使用了臨時 Bicep 文件，請考慮將修改整合到主要 Bicep 文件中。" -ForegroundColor Yellow
