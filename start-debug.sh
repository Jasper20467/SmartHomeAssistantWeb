#!/bin/bash

# Smart Home Assistant Debug Environment Launcher
# 智慧家庭助理調試環境啟動器

echo "🏠 Smart Home Assistant Debug Environment"
echo "=========================================="

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未運行，請先啟動 Docker"
    exit 1
fi

# 檢查 Docker Compose 是否可用
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ Docker Compose 未安裝"
    exit 1
fi

# 設定環境變數文件
if [ ! -f .env ]; then
    echo "📝 複製環境變數範本..."
    cp .env.debug .env
    echo "⚠️  請編輯 .env 文件設定您的 API 金鑰"
fi

echo "🚀 啟動 Debug 環境..."
docker-compose up -d

echo "⏳ 等待服務啟動..."
sleep 10

echo ""
echo "✅ Debug 環境已啟動！"
echo ""
echo "📡 服務端點："
echo "   • Backend API:    http://localhost:8000"
echo "   • Backend Docs:   http://localhost:8000/docs"
echo "   • LineBot API:    http://localhost:5000"
echo "   • Frontend:       http://localhost:4200"
echo "   • Database:       localhost:5432"
echo "   • Redis:          localhost:6379"
echo ""
echo "🐛 Debug 端點："
echo "   • Backend Debug:  localhost:5678"
echo "   • LineBot Debug:  localhost:5679"
echo ""
echo "🎯 VS Code Debug 設定："
echo "   1. 打開 VS Code Debug Panel (Ctrl+Shift+D)"
echo "   2. 選擇 'Backend API Debug (Docker)' 或 'LineBot API Debug (Docker)'"
echo "   3. 點擊開始調試 (F5)"
echo ""
echo "📋 常用命令："
echo "   • 查看日誌: docker-compose logs -f"
echo "   • 停止服務: docker-compose down"
echo "   • 重啟服務: docker-compose restart"
echo ""
echo "Happy Debugging! 🐛✨"
