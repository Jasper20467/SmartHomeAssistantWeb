#!/bin/bash

# 智能家居助手 EC2 部署腳本
# 此腳本用於在 EC2 上部署 Smart Home Assistant 專案
# 使用 docker-compose_fromHub.yml 從 DockerHub 拉取映像

echo "====== 智能家居助手 EC2 部署腳本 ======"
echo "開始部署過程..."

# 檢查是否已安裝 Docker
if ! command -v docker &> /dev/null; then
    echo "未檢測到 Docker，正在安裝..."
    # 安裝 Docker (Amazon Linux 2)
    sudo yum update -y
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ec2-user
    echo "Docker 安裝完成"
else
    echo "已檢測到 Docker"
fi

# 檢查是否已安裝 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "未檢測到 Docker Compose，正在安裝..."
    # 安裝 Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose 安裝完成"
else
    echo "已檢測到 Docker Compose"
fi

# 創建 docker-entrypoint-initdb.d 目錄
echo "創建數據庫初始化目錄..."
mkdir -p docker-entrypoint-initdb.d

# 創建 init.sql 文件
echo "創建數據庫初始化腳本..."
cat > docker-entrypoint-initdb.d/init.sql << 'EOL'
-- Database initialization script
CREATE DATABASE smarthome;

\c smarthome;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add additional initialization SQL here if needed
EOL

# 檢查當前目錄是否有 docker-compose_fromHub.yml 文件
if [ ! -f "docker-compose_fromHub.yml" ]; then
    echo "警告: 在當前目錄找不到 docker-compose_fromHub.yml 文件！"
    
    # 獲取腳本所在目錄
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
    
    # 檢查腳本目錄和專案根目錄中是否有 docker-compose_fromHub.yml 文件
    if [ -f "$SCRIPT_DIR/docker-compose_fromHub.yml" ]; then
        echo "在腳本目錄找到 docker-compose_fromHub.yml 文件，將使用該檔案..."
        cp "$SCRIPT_DIR/docker-compose_fromHub.yml" ./docker-compose_fromHub.yml
    elif [ -f "$PROJECT_ROOT/docker-compose_fromHub.yml" ]; then
        echo "在專案根目錄找到 docker-compose_fromHub.yml 文件，將使用該檔案..."
        cp "$PROJECT_ROOT/docker-compose_fromHub.yml" ./docker-compose_fromHub.yml
    else
        echo "錯誤: 找不到 docker-compose_fromHub.yml 文件！請確保文件位於當前目錄、腳本目錄或專案根目錄。"
        exit 1
    fi
fi

echo "使用當前目錄的 docker-compose_fromHub.yml 文件"

# 創建 .env 文件以設置環境變數
echo "創建 .env 配置文件..."
cat > .env << 'EOL'
# LINE Bot 配置
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
# Google Gemini 配置
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
EOL

echo "請編輯 .env 文件以設置您的 LINE 頻道訪問令牌和 Gemini API 金鑰"
echo "使用以下命令:"
echo "nano .env"

# 拉取映像並啟動容器
echo "拉取映像並啟動容器..."
docker-compose -f docker-compose_fromHub.yml up -d

# 檢查容器狀態
echo "檢查容器狀態..."
docker-compose -f docker-compose_fromHub.yml ps

# 顯示訪問信息
# 使用 IMDSv2 安全地獲取 EC2 公共 IP
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" 2>/dev/null || echo "")
if [ -n "$TOKEN" ]; then
    PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")
else
    # 如果 IMDSv2 不可用，回退到直接方式或其他方法獲取 IP
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || curl -s -4 ifconfig.me || curl -s -4 icanhazip.com || echo "無法確定 IP")
fi

echo ""
echo "===================================================="
echo "部署完成！您可以通過以下URL訪問服務："
echo ""
echo "🌐 主要訪問方式（推薦）："
echo "   網站: https://smarthome.the-jasperezlife.com"
echo "   (透過 Caddy 反向代理，支援 SSL)"
echo ""
echo "🔧 直接IP訪問（備用）："
echo "   前端界面: http://$PUBLIC_IP (透過 Caddy)"
echo "   DATABASE: $PUBLIC_IP:5432"
echo ""
echo "📋 內部服務 (僅限容器間通信)："
echo "   Frontend: frontend:80"
echo "   Backend API: backend:8000"
echo "   LineBot: linebot:5000"
echo "   Database: db:5432"
echo ""
echo "🤖 LINE Bot 路由："
echo "   Webhook: https://smarthome.the-jasperezlife.com/webhook"
echo "   Debug API: https://smarthome.the-jasperezlife.com/api/debug/*"
echo "   Backend 連接測試: https://smarthome.the-jasperezlife.com/api/debug/backend"
echo "   配置檢查: https://smarthome.the-jasperezlife.com/api/debug/config"
echo "   LineBot 路由: https://smarthome.the-jasperezlife.com/linebot/*"
echo "===================================================="
echo ""
echo "🔒 SSL 憑證資訊："
echo "   Caddy 會自動從 Let's Encrypt 取得 SSL 憑證"
echo "   首次訪問可能需要等待憑證生成"
echo ""
echo "📝 注意事項："
echo "   1. 確保域名 smarthome.the-jasperezlife.com 指向此 EC2 實例"
echo "   2. 確保安全組開放 80 和 443 端口"
echo "   3. 設定 LINE Bot Webhook URL: https://smarthome.the-jasperezlife.com/webhook"
echo "   4. 在 .env 檔案中設定 LINE_CHANNEL_ACCESS_TOKEN 和 GEMINI_API_KEY"
echo "   5. 如需查看 Caddy 日誌：docker-compose -f docker-compose_fromHub.yml logs -f caddy"
echo "===================================================="
echo "如果您需要查看容器日誌，請運行:"
echo "docker-compose -f docker-compose_fromHub.yml logs -f [服務名稱]"
echo ""
echo "要停止所有容器，請運行:"
echo "docker-compose -f docker-compose_fromHub.yml down"
echo "===================================================="
