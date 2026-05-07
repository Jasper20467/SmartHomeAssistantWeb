@echo off
REM Smart Home Assistant Debug Environment Launcher (Windows)
REM 智慧家庭助理調試環境啟動器 (Windows)

echo 🏠 Smart Home Assistant Debug Environment
echo ==========================================

REM 檢查 Docker 是否運行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未運行，請先啟動 Docker
    pause
    exit /b 1
)

REM 檢查 Docker Compose 是否可用
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安裝
    pause
    exit /b 1
)

REM 設定環境變數文件
if not exist .env (
    echo 📝 複製環境變數範本...
    copy .env.debug .env >nul
    echo ⚠️  請編輯 .env 文件設定您的 API 金鑰
)

echo 🚀 啟動 Debug 環境...
docker-compose up -d

echo ⏳ 等待服務啟動...
timeout /t 10 /nobreak >nul

echo.
echo ✅ Debug 環境已啟動！
echo.
echo 📡 服務端點：
echo    • Backend API:    http://localhost:8000
echo    • Backend Docs:   http://localhost:8000/docs
echo    • LineBot API:    http://localhost:5000
echo    • Frontend:       http://localhost:4200
echo    • Database:       localhost:5432
echo    • Redis:          localhost:6379
echo.
echo 🐛 Debug 端點：
echo    • Backend Debug:  localhost:5678
echo    • LineBot Debug:  localhost:5679
echo.
echo 🎯 VS Code Debug 設定：
echo    1. 打開 VS Code Debug Panel (Ctrl+Shift+D)
echo    2. 選擇 'Backend API Debug (Docker)' 或 'LineBot API Debug (Docker)'
echo    3. 點擊開始調試 (F5)
echo.
echo 📋 常用命令：
echo    • 查看日誌: docker-compose logs -f
echo    • 停止服務: docker-compose down
echo    • 重啟服務: docker-compose restart
echo.
echo Happy Debugging! 🐛✨
echo.
pause
