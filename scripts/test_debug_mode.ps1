# Debug Mode 整合測試腳本 (PowerShell 版本)

Write-Host "🏠 Smart Home Assistant Debug Mode 整合測試" -ForegroundColor Magenta
Write-Host "=================================================" -ForegroundColor Blue

# 檢查是否有運行中的容器
Write-Host "🔍 檢查現有容器..." -ForegroundColor Cyan
$runningContainers = docker-compose ps --services --filter "status=running" 2>$null
if ($runningContainers) {
    Write-Host "⚠️  發現運行中的容器，正在停止..." -ForegroundColor Yellow
    docker-compose down
}

# 清理舊的映像和容器
Write-Host "🧹 清理環境..." -ForegroundColor Cyan
docker-compose down --volumes --remove-orphans 2>$null

# 建置並啟動服務
Write-Host "🔨 建置並啟動服務..." -ForegroundColor Cyan
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 服務啟動失敗" -ForegroundColor Red
    exit 1
}

# 等待服務啟動
Write-Host "⏳ 等待服務啟動..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 檢查容器狀態
Write-Host "📋 檢查容器狀態..." -ForegroundColor Cyan
docker-compose ps

# 等待資料庫初始化
Write-Host "💾 等待資料庫初始化..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 檢查服務日誌
Write-Host "📜 檢查服務日誌..." -ForegroundColor Cyan

Write-Host "--- Backend 日誌 ---" -ForegroundColor Green
docker-compose logs --tail=10 backend

Write-Host "--- LineBot 日誌 ---" -ForegroundColor Green
docker-compose logs --tail=10 linebot

Write-Host "--- Frontend 日誌 ---" -ForegroundColor Green
docker-compose logs --tail=10 frontend

Write-Host "--- Database 日誌 ---" -ForegroundColor Green
docker-compose logs --tail=10 db

# 執行整合測試
Write-Host "🧪 執行整合測試..." -ForegroundColor Cyan
python scripts/test_integration.py --mode debug --output test_results_debug.json

if ($LASTEXITCODE -eq 0) {
    Write-Host "=================================================" -ForegroundColor Blue
    Write-Host "✅ Debug Mode 測試完成" -ForegroundColor Green
    Write-Host "📊 詳細結果請查看: test_results_debug.json" -ForegroundColor Cyan
} else {
    Write-Host "=================================================" -ForegroundColor Blue
    Write-Host "❌ Debug Mode 測試失敗" -ForegroundColor Red
    Write-Host "📊 詳細結果請查看: test_results_debug.json" -ForegroundColor Cyan
    exit 1
}
