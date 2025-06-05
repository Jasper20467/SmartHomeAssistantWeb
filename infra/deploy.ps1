param (
    [string]$resourceGroupName = "JYSmartHomeAssistant",
    [string]$location = "eastasia",
    [string]$appName = "JYHomeAssistant",
    [string]$acrName = "jasperbasicacr",
    [string]$acrPassword = "",
    [string]$dbPassword = "YourSecurePassword123!",
    [string]$imageTag = "1.0"
)

# 顯示歡迎訊息
Write-Host "====== JYHomeAssistant 部署腳本 (Container Apps 版) ======" -ForegroundColor Green
Write-Host "此腳本將幫助您將 JYHomeAssistant 部署到 Azure Container Apps" -ForegroundColor Green
Write-Host ""

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

# 檢查 ACR 密碼是否提供
if ([string]::IsNullOrEmpty($acrPassword)) {
    # 嘗試使用 Azure CLI 獲取 ACR 密碼
    Write-Host "嘗試從 Azure 獲取 ACR 密碼..." -ForegroundColor Yellow
    try {
        $acrPassword = az acr credential show --name $acrName --query "passwords[0].value" -o tsv
        if ([string]::IsNullOrEmpty($acrPassword)) {
            throw "無法自動獲取 ACR 密碼"
        }
        Write-Host "已成功獲取 ACR 密碼。" -ForegroundColor Green
    } catch {
        Write-Host "無法自動獲取 ACR 密碼，請手動輸入。" -ForegroundColor Yellow
        $securePassword = Read-Host -AsSecureString "請輸入 ACR 密碼(輸入將被隱藏)"
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        $acrPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
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

# 預覽部署
Write-Host "預覽 Bicep 部署..." -ForegroundColor Yellow
az deployment group what-if `
    --resource-group $resourceGroupName `
    --template-file ./main.bicep `
    --parameters appName=$appName `
    --parameters acrName=$acrName `
    --parameters dbPassword=$dbPassword `
    --parameters acrPassword=$acrPassword `
    --parameters imageVersion=$imageTag

$confirm = Read-Host "是否繼續部署? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "已取消部署。" -ForegroundColor Yellow
    exit 0
}

# 部署 Bicep 模板
Write-Host "開始部署 Bicep 模板..." -ForegroundColor Yellow
$deploymentOutput = az deployment group create `
    --resource-group $resourceGroupName `
    --template-file ./main.bicep `
    --parameters appName=$appName `
    --parameters acrName=$acrName `
    --parameters dbPassword=$dbPassword `
    --parameters acrPassword=$acrPassword `
    --parameters imageVersion=$imageTag `
    --query "properties.outputs" -o json

if ($LASTEXITCODE -ne 0) {
    Write-Host "部署失敗，請檢查錯誤訊息。" -ForegroundColor Red
    exit 1
}

# 解析部署輸出
$outputs = $deploymentOutput | ConvertFrom-Json
$frontendUrl = $outputs.frontendUrl.value
$backendUrl = $outputs.backendUrl.value
# LineBot URL 已被註解，所以不再獲取
# $linebotUrl = $outputs.linebotUrl.value

# 輸出部署結果
Write-Host "部署成功完成！" -ForegroundColor Green
Write-Host "===================== 應用程式網址 =====================" -ForegroundColor Cyan
Write-Host "前端應用: $frontendUrl" -ForegroundColor White
Write-Host "後端API: $backendUrl" -ForegroundColor White
# 註解掉 LineBot URL 顯示
# Write-Host "LineBot: $linebotUrl" -ForegroundColor White
Write-Host "註: LineBot 服務暫時未部署" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan