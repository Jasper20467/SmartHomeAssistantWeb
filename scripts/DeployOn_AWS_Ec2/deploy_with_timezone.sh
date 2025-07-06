#!/bin/bash

# AWS EC2 Docker 部署腳本 - 包含時區設定
# 作者：Smart Home Assistant 團隊
# 版本：1.0

echo "🚀 開始部署 Smart Home Assistant 到 AWS EC2..."

# 檢查是否為 root 用戶
if [[ $EUID -eq 0 ]]; then
   echo "❌ 請不要以 root 用戶身份運行此腳本"
   exit 1
fi

# 檢查必要的工具
echo "🔍 檢查必要的工具..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 檢查系統時區設定
echo "🕐 檢查系統時區設定..."
CURRENT_TZ=$(timedatectl show --property=Timezone --value 2>/dev/null || echo "Unknown")
echo "當前系統時區：$CURRENT_TZ"

# 建議設定時區為 Asia/Taipei
if [ "$CURRENT_TZ" != "Asia/Taipei" ]; then
    echo "⚠️  建議將系統時區設定為 Asia/Taipei"
    echo "您可以使用以下命令設定："
    echo "sudo timedatectl set-timezone Asia/Taipei"
    
    read -p "是否要自動設定時區為 Asia/Taipei？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v timedatectl &> /dev/null; then
            sudo timedatectl set-timezone Asia/Taipei
            echo "✅ 時區已設定為 Asia/Taipei"
        else
            echo "⚠️  timedatectl 不可用，請手動設定時區"
        fi
    else
        echo "⚠️  請手動設定時區，或確認現有時區設定正確"
    fi
fi

# 注意：我們已改用 Dockerfile 內建時區設定，不再需要掛載時區檔案
echo "📝 注意：此版本使用 Dockerfile 內建時區設定，不需要掛載 /etc/timezone 和 /etc/localtime 檔案"

# 檢查環境變數檔案
echo "🔍 檢查環境變數..."
if [ ! -f .env ]; then
    echo "⚠️  .env 檔案不存在，正在創建範例檔案..."
    cat > .env << EOF
# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
CHATGPT_API_KEY=your_chatgpt_api_key_here

# 時區設定
TZ=Asia/Taipei

# 資料庫設定
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=smarthome
EOF
    echo "✅ 已創建 .env 檔案範例，請編輯並填入正確的值"
fi

# 停止現有的容器
echo "🛑 停止現有容器..."
docker-compose -f docker-compose_fromHub.yml down

# 拉取最新的映像檔
echo "📥 拉取最新映像檔..."
docker-compose -f docker-compose_fromHub.yml pull

# 啟動服務
echo "🚀 啟動服務..."
docker-compose -f docker-compose_fromHub.yml up -d

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
sleep 10
docker-compose -f docker-compose_fromHub.yml ps

# 檢查容器內的時區設定
echo "🕐 檢查容器內的時區設定..."
echo "Frontend 容器時區："
docker-compose -f docker-compose_fromHub.yml exec -T frontend date
echo "Backend 容器時區："
docker-compose -f docker-compose_fromHub.yml exec -T backend date
echo "Database 容器時區："
docker-compose -f docker-compose_fromHub.yml exec -T db date

# 檢查日誌
echo "📋 檢查最近的日誌..."
docker-compose -f docker-compose_fromHub.yml logs --tail=50

echo "✅ 部署完成！"
echo "📱 Frontend: http://localhost:80"
echo "🔧 Backend API: http://localhost:8000"
echo "🤖 LineBot: http://localhost:5000"
echo "🗄️  Database: localhost:5432"
echo ""
echo "📝 提示："
echo "1. 請確保所有服務都在運行"
echo "2. 檢查日誌是否有錯誤訊息"
echo "3. 確認時區設定正確"
echo "4. 編輯 .env 檔案以設定正確的 API 金鑰"
