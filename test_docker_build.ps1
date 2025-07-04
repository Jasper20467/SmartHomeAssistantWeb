# 測試 Docker 建置腳本
param(
    [switch]$Clean = $false,
    [switch]$NoBuild = $false
)

Write-Host "開始測試 Docker 建置流程..." -ForegroundColor Green

# 設定變數
$FrontendPath = "frontend"
$DockerFile = "docker\frontend.Dockerfile"
$ImageName = "smart-home-frontend-test"
$ContainerName = "smart-home-frontend-test-container"

# 清理舊容器和映像
if ($Clean) {
    Write-Host "清理舊容器和映像..." -ForegroundColor Yellow
    docker stop $ContainerName -ErrorAction SilentlyContinue
    docker rm $ContainerName -ErrorAction SilentlyContinue
    docker rmi $ImageName -ErrorAction SilentlyContinue
}

# 建置 Docker 映像
if (-not $NoBuild) {
    Write-Host "建置 Docker 映像..." -ForegroundColor Yellow
    docker build -t $ImageName -f $DockerFile $FrontendPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker 建置失敗!" -ForegroundColor Red
        exit 1
    }
}

# 執行容器
Write-Host "啟動測試容器..." -ForegroundColor Yellow
docker run -d --name $ContainerName -p 8080:80 $ImageName

if ($LASTEXITCODE -ne 0) {
    Write-Host "容器啟動失敗!" -ForegroundColor Red
    exit 1
}

# 等待容器啟動
Write-Host "等待容器啟動..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 檢查容器狀態
$ContainerStatus = docker inspect $ContainerName --format='{{.State.Status}}'
Write-Host "容器狀態: $ContainerStatus" -ForegroundColor Cyan

if ($ContainerStatus -eq "running") {
    Write-Host "✓ 容器成功啟動!" -ForegroundColor Green
    Write-Host "測試網址: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "請在瀏覽器中檢查月曆組件是否正常顯示" -ForegroundColor Yellow
    
    # 檢查容器日誌
    Write-Host "`n容器日誌:" -ForegroundColor Yellow
    docker logs $ContainerName
    
    Write-Host "`n輸入任意鍵停止容器..." -ForegroundColor Yellow
    Read-Host
    
    # 停止並移除容器
    docker stop $ContainerName
    docker rm $ContainerName
    
    Write-Host "測試完成!" -ForegroundColor Green
} else {
    Write-Host "✗ 容器啟動失敗!" -ForegroundColor Red
    Write-Host "錯誤日誌:" -ForegroundColor Yellow
    docker logs $ContainerName
    
    # 清理失敗的容器
    docker rm $ContainerName -ErrorAction SilentlyContinue
}
