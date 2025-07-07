#!/bin/bash

# Debug Mode 整合測試腳本

set -e

echo "🏠 Smart Home Assistant Debug Mode 整合測試"
echo "================================================="

# 檢查是否有運行中的容器
echo "🔍 檢查現有容器..."
if docker-compose ps | grep -q "Up"; then
    echo "⚠️  發現運行中的容器，正在停止..."
    docker-compose down
fi

# 清理舊的映像和容器
echo "🧹 清理環境..."
docker-compose down --volumes --remove-orphans 2>/dev/null || true

# 建置並啟動服務
echo "🔨 建置並啟動服務..."
docker-compose up -d --build

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 30

# 檢查容器狀態
echo "📋 檢查容器狀態..."
docker-compose ps

# 等待資料庫初始化
echo "💾 等待資料庫初始化..."
sleep 10

# 檢查服務日誌
echo "📜 檢查服務日誌..."
echo "--- Backend 日誌 ---"
docker-compose logs --tail=10 backend

echo "--- LineBot 日誌 ---"
docker-compose logs --tail=10 linebot

echo "--- Frontend 日誌 ---"
docker-compose logs --tail=10 frontend

echo "--- Database 日誌 ---"
docker-compose logs --tail=10 db

# 執行整合測試
echo "🧪 執行整合測試..."
python scripts/test_integration.py --mode debug --output test_results_debug.json

echo "================================================="
echo "✅ Debug Mode 測試完成"
echo "📊 詳細結果請查看: test_results_debug.json"
