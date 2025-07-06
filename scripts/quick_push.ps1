# 快速 Docker 推送腳本 (簡化版)
# 使用方法：.\quick_push.ps1 [版本號]

param(
    [string]$Version = (Get-Date -Format "yyyy.MM.dd.HHmm")
)

# Docker Hub 設定
$DOCKER_USERNAME = "popo510691"

# 映像配置
$services = @(
    @{ name = "frontend"; image = "homeassistant.frontend"; dockerfile = "docker/frontend.Dockerfile"; context = "./frontend" },
    @{ name = "backend"; image = "homeassistant.backend"; dockerfile = "docker/backend.Dockerfile"; context = "./backend" },
    @{ name = "linebot"; image = "homeassistant.linebot"; dockerfile = "docker/linebot.Dockerfile"; context = "." }
)

Write-Host "🚀 快速推送 Docker 映像到 Docker Hub" -ForegroundColor Magenta
Write-Host "版本號: $Version" -ForegroundColor Blue
Write-Host ""

# 確認推送
$confirm = Read-Host "是否繼續？(Y/n)"
if ($confirm -match "^[Nn]$") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit
}

$startTime = Get-Date
$failed = @()
$success = @()

foreach ($service in $services) {
    $imageName = "$DOCKER_USERNAME/$($service.image)"
    
    Write-Host "📦 處理 $($service.name)..." -ForegroundColor Cyan
    
    try {
        # 建置
        Write-Host "   🔨 建置中..." -ForegroundColor Yellow
        docker build -f $service.dockerfile -t "$imageName`:$Version" -t "$imageName`:latest" $service.context | Out-Null
        
        # 推送版本號標籤
        Write-Host "   📤 推送 $Version..." -ForegroundColor Yellow
        docker push "$imageName`:$Version" | Out-Null
        
        # 推送 latest 標籤
        Write-Host "   📤 推送 latest..." -ForegroundColor Yellow
        docker push "$imageName`:latest" | Out-Null
        
        Write-Host "   ✅ 完成" -ForegroundColor Green
        $success += $service.name
    }
    catch {
        Write-Host "   ❌ 失敗: $($_.Exception.Message)" -ForegroundColor Red
        $failed += $service.name
    }
    Write-Host ""
}

$duration = (Get-Date) - $startTime
Write-Host "⏱️ 總耗時: $([math]::Round($duration.TotalMinutes, 1)) 分鐘" -ForegroundColor Blue

if ($success.Count -gt 0) {
    Write-Host "✅ 成功: $($success -join ', ')" -ForegroundColor Green
}

if ($failed.Count -gt 0) {
    Write-Host "❌ 失敗: $($failed -join ', ')" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔗 Docker Hub: https://hub.docker.com/u/$DOCKER_USERNAME" -ForegroundColor Cyan
