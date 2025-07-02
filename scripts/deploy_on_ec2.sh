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
CHATGPT_API_KEY=your_chatgpt_api_key_here
EOL

echo "請編輯 .env 文件以設置您的 LINE 頻道訪問令牌和 ChatGPT API 密鑰"
echo "使用以下命令:"
echo "nano .env"

# 拉取映像並啟動容器
echo "拉取映像並啟動容器..."
docker-compose -f docker-compose_fromHub.yml up -d

# 檢查容器狀態
echo "檢查容器狀態..."
docker-compose -f docker-compose_fromHub.yml ps

# 顯示訪問信息
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo ""
echo "===================================================="
echo "部署完成！您可以通過以下URL訪問服務："
echo "前端界面: http://$PUBLIC_IP"
echo "後端 API: http://$PUBLIC_IP:8000"
echo "LINE Bot: http://$PUBLIC_IP:5000"
echo "===================================================="
echo "如果您需要查看容器日誌，請運行:"
echo "docker-compose -f docker-compose_fromHub.yml logs -f [服務名稱]"
echo ""
echo "要停止所有容器，請運行:"
echo "docker-compose -f docker-compose_fromHub.yml down"
echo "===================================================="
