# Smart Home Assistant Docker Images Build and Push Script (PowerShell)
# 自動建置並推送所有 Docker 映像到 Docker Hub
# 
# 使用方法：
# .\push_docker_images.ps1 [版本號]
# 
# 範例：
# .\push_docker_images.ps1 1.1
# .\push_docker_images.ps1 latest

param(
    [string]$Version = "latest"
)

# 設定錯誤處理
$ErrorActionPreference = "Stop"

# Docker Hub 設定
$DOCKER_USERNAME = "popo510691"
$REGISTRY = "docker.io"

# 映像名稱配置
$IMAGES = @{
    "frontend" = "homeassistant.frontend"
    "backend"  = "homeassistant.backend"
    "linebot"  = "homeassistant.linebot"
}

# Dockerfile 路徑配置
$DOCKERFILES = @{
    "frontend" = "docker/frontend.Dockerfile"
    "backend"  = "docker/backend.Dockerfile"
    "linebot"  = "docker/linebot.Dockerfile"
}

# 建置上下文配置
$BUILD_CONTEXTS = @{
    "frontend" = "./frontend"
    "backend"  = "./backend"
    "linebot"  = "."
}

# 顏色函數
function Write-ColoredText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red"     = "Red"
        "Green"   = "Green"
        "Yellow"  = "Yellow"
        "Blue"    = "Blue"
        "Purple"  = "Magenta"
        "Cyan"    = "Cyan"
        "White"   = "White"
    }
    
    Write-Host $Text -ForegroundColor $colorMap[$Color]
}

# 顯示標題
Write-ColoredText "=================================================" "Purple"
Write-ColoredText "  Smart Home Assistant Docker Build & Push" "Purple"
Write-ColoredText "=================================================" "Purple"
Write-Host ""

Write-ColoredText "📦 建置版本：$Version" "Blue"
Write-Host ""

# 檢查是否已登入 Docker Hub
Write-ColoredText "🔐 檢查 Docker Hub 登入狀態..." "Yellow"
try {
    $dockerInfo = docker info 2>&1
    if ($dockerInfo -notmatch "Username: $DOCKER_USERNAME") {
        Write-ColoredText "❌ 尚未登入 Docker Hub，請先執行：docker login" "Red"
        exit 1
    }
    Write-ColoredText "✅ 已登入 Docker Hub (用戶: $DOCKER_USERNAME)" "Green"
}
catch {
    Write-ColoredText "❌ 無法取得 Docker 資訊，請確認 Docker 是否正常運行" "Red"
    exit 1
}
Write-Host ""

# 檢查 Docker 是否運行
Write-ColoredText "🐳 檢查 Docker 服務..." "Yellow"
try {
    docker info | Out-Null
    Write-ColoredText "✅ Docker 服務正常運行" "Green"
}
catch {
    Write-ColoredText "❌ Docker 服務未運行，請先啟動 Docker" "Red"
    exit 1
}
Write-Host ""

# 檢查必要檔案
Write-ColoredText "📁 檢查必要檔案..." "Yellow"
foreach ($service in $DOCKERFILES.Keys) {
    $dockerfile = $DOCKERFILES[$service]
    $context = $BUILD_CONTEXTS[$service]
    
    if (-not (Test-Path $dockerfile)) {
        Write-ColoredText "❌ Dockerfile 不存在: $dockerfile" "Red"
        exit 1
    }
    
    if (-not (Test-Path $context -PathType Container)) {
        Write-ColoredText "❌ 建置上下文目錄不存在: $context" "Red"
        exit 1
    }
}
Write-ColoredText "✅ 所有必要檔案都存在" "Green"
Write-Host ""

# 清理舊的映像（可選）
Write-Host "🧹 是否要清理舊的本地映像？(y/N): " -ForegroundColor Yellow -NoNewline
$cleanup = Read-Host
if ($cleanup -match "^[Yy]$") {
    Write-ColoredText "🧹 清理舊的本地映像..." "Yellow"
    foreach ($service in $IMAGES.Keys) {
        $imageName = "$DOCKER_USERNAME/$($IMAGES[$service])"
        try {
            docker rmi "$imageName`:latest" 2>$null
            docker rmi "$imageName`:$Version" 2>$null
        }
        catch {
            # 忽略錯誤，映像可能不存在
        }
    }
    Write-ColoredText "✅ 清理完成" "Green"
}
Write-Host ""

# 建置和推送函數
function Build-And-Push {
    param(
        [string]$Service
    )
    
    $imageName = "$DOCKER_USERNAME/$($IMAGES[$Service])"
    $dockerfile = $DOCKERFILES[$Service]
    $context = $BUILD_CONTEXTS[$Service]
    
    Write-ColoredText "🏗️  建置 $Service 映像..." "Purple"
    Write-ColoredText "   映像名稱: $imageName`:$Version" "Cyan"
    Write-ColoredText "   Dockerfile: $dockerfile" "Cyan"
    Write-ColoredText "   建置上下文: $context" "Cyan"
    
    try {
        # 建置映像
        Write-ColoredText "🔨 開始建置..." "Yellow"
        docker build -f $dockerfile -t "$imageName`:$Version" $context
        Write-ColoredText "✅ $Service 建置成功" "Green"
        
        # 如果版本不是 latest，也標記為 latest
        if ($Version -ne "latest") {
            docker tag "$imageName`:$Version" "$imageName`:latest"
            Write-ColoredText "✅ 已標記為 latest" "Green"
        }
        
        # 推送映像
        Write-ColoredText "📤 推送 $Service 映像到 Docker Hub..." "Yellow"
        docker push "$imageName`:$Version"
        Write-ColoredText "✅ $Service 推送成功" "Green"
        
        # 推送 latest 標籤
        if ($Version -ne "latest") {
            docker push "$imageName`:latest"
            Write-ColoredText "✅ $Service latest 標籤推送成功" "Green"
        }
        
        return $true
    }
    catch {
        Write-ColoredText "❌ $Service 建置或推送失敗: $($_.Exception.Message)" "Red"
        return $false
    }
    finally {
        Write-Host ""
    }
}

# 顯示建置計劃
Write-ColoredText "📋 建置計劃：" "Blue"
foreach ($service in $IMAGES.Keys) {
    $imageName = "$DOCKER_USERNAME/$($IMAGES[$service])"
    Write-ColoredText "   • $service -> $imageName`:$Version" "Cyan"
}
Write-Host ""

# 確認開始建置
Write-Host "🚀 是否開始建置並推送所有映像？(Y/n): " -ForegroundColor Yellow -NoNewline
$confirm = Read-Host
if ($confirm -match "^[Nn]$") {
    Write-ColoredText "⏹️  作業已取消" "Yellow"
    exit 0
}

# 記錄開始時間
$startTime = Get-Date

# 建置所有映像
Write-ColoredText "🚀 開始建置和推送所有映像..." "Purple"
Write-Host ""

$failedServices = @()
$successfulServices = @()

foreach ($service in $IMAGES.Keys) {
    Write-ColoredText "========================================" "Blue"
    Write-ColoredText "處理服務: $service" "Blue"
    Write-ColoredText "========================================" "Blue"
    
    if (Build-And-Push -Service $service) {
        $successfulServices += $service
    }
    else {
        $failedServices += $service
        Write-ColoredText "❌ $service 處理失敗，繼續處理下一個服務..." "Red"
    }
}

# 計算執行時間
$endTime = Get-Date
$duration = $endTime - $startTime
$minutes = [math]::Floor($duration.TotalMinutes)
$seconds = $duration.Seconds

# 顯示總結
Write-ColoredText "=================================================" "Purple"
Write-ColoredText "  建置和推送完成總結" "Purple"
Write-ColoredText "=================================================" "Purple"
Write-Host ""
Write-ColoredText "⏱️  總執行時間: $minutes 分 $seconds 秒" "Blue"
Write-ColoredText "📦 目標版本: $Version" "Blue"
Write-Host ""

if ($successfulServices.Count -gt 0) {
    Write-ColoredText "✅ 成功的服務 ($($successfulServices.Count))：" "Green"
    foreach ($service in $successfulServices) {
        $imageName = "$DOCKER_USERNAME/$($IMAGES[$service])"
        Write-ColoredText "   • $service -> $imageName`:$Version" "Green"
    }
    Write-Host ""
}

if ($failedServices.Count -gt 0) {
    Write-ColoredText "❌ 失敗的服務 ($($failedServices.Count))：" "Red"
    foreach ($service in $failedServices) {
        Write-ColoredText "   • $service" "Red"
    }
    Write-Host ""
}

# 顯示 Docker Hub 連結
if ($successfulServices.Count -gt 0) {
    Write-ColoredText "🔗 Docker Hub 連結：" "Cyan"
    foreach ($service in $successfulServices) {
        $imageName = $IMAGES[$service]
        Write-ColoredText "   • https://hub.docker.com/r/$DOCKER_USERNAME/$imageName" "Cyan"
    }
    Write-Host ""
}

# 顯示使用說明
Write-ColoredText "📖 使用新映像：" "Yellow"
Write-ColoredText "   • 更新 docker-compose.yml 中的版本號為 $Version" "Cyan"
Write-ColoredText "   • 或執行：docker-compose pull 拉取最新映像" "Cyan"
Write-Host ""

# 提供更新配置檔案的選項
if ($successfulServices.Count -gt 0 -and $Version -ne "latest") {
    Write-Host "🔄 是否要自動更新 AWS EC2 部署配置檔案的版本號？(y/N): " -ForegroundColor Yellow -NoNewline
    $updateConfig = Read-Host
    if ($updateConfig -match "^[Yy]$") {
        $configFile = "scripts\DeployOn_AWS_Ec2\docker-compose_fromHub.yml"
        if (Test-Path $configFile) {
            Write-ColoredText "🔄 更新配置檔案..." "Yellow"
            
            # 備份原檔案
            Copy-Item $configFile "$configFile.backup"
            
            # 讀取檔案內容
            $content = Get-Content $configFile -Raw
            
            # 更新版本號
            foreach ($service in $successfulServices) {
                $imageName = $IMAGES[$service]
                $pattern = "$DOCKER_USERNAME/$imageName`:[\w\.]+"
                $replacement = "$DOCKER_USERNAME/$imageName`:$Version"
                $content = $content -replace $pattern, $replacement
            }
            
            # 寫回檔案
            Set-Content $configFile $content -NoNewline
            
            Write-ColoredText "✅ 配置檔案已更新：$configFile" "Green"
            Write-ColoredText "💾 備份檔案：$configFile.backup" "Yellow"
        }
        else {
            Write-ColoredText "❌ 配置檔案不存在：$configFile" "Red"
        }
    }
}

# 最終狀態
if ($failedServices.Count -eq 0) {
    Write-ColoredText "🎉 所有映像建置和推送成功完成！" "Green"
    exit 0
}
else {
    Write-ColoredText "⚠️  部分映像建置或推送失敗，請檢查上述錯誤訊息" "Yellow"
    exit 1
}
