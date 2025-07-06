@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo   Smart Home Assistant Docker Push
echo ============================================
echo.

:: 檢查 PowerShell 是否可用
powershell -Command "Write-Host 'PowerShell is available'" >nul 2>&1
if errorlevel 1 (
    echo Error: PowerShell is not available
    pause
    exit /b 1
)

:: 檢查腳本檔案是否存在
if not exist "scripts\quick_push.ps1" (
    echo Error: quick_push.ps1 not found
    pause
    exit /b 1
)

:: 提示選擇
echo 請選擇操作：
echo.
echo [1] 快速推送 (自動版本號)
echo [2] 快速推送 (指定版本號)
echo [3] 完整推送 (含所有功能)
echo [4] 退出
echo.
set /p choice="請輸入選項 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 執行快速推送 (自動版本號)...
    powershell -ExecutionPolicy Bypass -File "scripts\quick_push.ps1"
) else if "%choice%"=="2" (
    echo.
    set /p version="請輸入版本號: "
    echo 執行快速推送 (版本: !version!)...
    powershell -ExecutionPolicy Bypass -File "scripts\quick_push.ps1" -Version "!version!"
) else if "%choice%"=="3" (
    echo.
    set /p version="請輸入版本號 (留空使用 latest): "
    if "!version!"=="" set version=latest
    echo 執行完整推送 (版本: !version!)...
    powershell -ExecutionPolicy Bypass -File "scripts\push_docker_images.ps1" -Version "!version!"
) else if "%choice%"=="4" (
    echo 已退出
    exit /b 0
) else (
    echo 無效的選項
    pause
    exit /b 1
)

echo.
echo 操作完成
pause
