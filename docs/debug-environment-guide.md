# Debug Environment Setup Guide

這是一個完整的 Docker 容器化本地開發和調試環境，支援 VS Code remote debugging。

## 📋 環境概述

### 🚀 服務清單
- **Backend API** (FastAPI) - 端口 8000, Debug 端口 5678
- **LineBot AI** (Flask) - 端口 5000, Debug 端口 5679
- **Frontend** (Angular) - 端口 4200
- **PostgreSQL** - 端口 5432
- **Redis** (可選) - 端口 6379

### 🎯 特色功能
- ✅ VS Code Remote Debugging 支援
- ✅ 代碼熱重載 (Hot Reload)
- ✅ 容器間網路通訊
- ✅ 資料卷持久化
- ✅ 健康檢查機制
- ✅ 完整的開發工具鏈

## 🛠️ 快速開始

### 1. 環境準備
```bash
# 複製環境變數範本
cp .env.debug .env

# 編輯環境變數，設定您的 API 金鑰
code .env
```

### 2. 啟動 Debug 環境
```bash
# 啟動所有服務
docker-compose -f docker-compose_debug.yml up -d

# 或使用 VS Code Task (Ctrl+Shift+P -> Tasks: Run Task)
# 選擇 "Start All Debug Containers"
```

### 3. VS Code Debug 設定

#### 方法一：使用 VS Code Debug Panel
1. 打開 VS Code Debug Panel (Ctrl+Shift+D)
2. 選擇 debug 配置：
   - **Backend API Debug (Docker)** - 僅調試 Backend
   - **LineBot API Debug (Docker)** - 僅調試 LineBot
   - **Debug Backend + LineBot** - 同時調試兩個服務

#### 方法二：使用 Command Palette
1. 按 `Ctrl+Shift+P`
2. 輸入 "Debug: Select and Start Debugging"
3. 選擇相應的 debug 配置

## 🔧 詳細配置

### Backend Debug 配置
```json
{
    "name": "Backend API Debug (Docker)",
    "type": "debugpy",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}/backend",
            "remoteRoot": "/app"
        }
    ]
}
```

### LineBot Debug 配置
```json
{
    "name": "LineBot API Debug (Docker)",
    "type": "debugpy",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5679
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}/LineBotAI",
            "remoteRoot": "/app"
        }
    ]
}
```

## 📡 服務端點

### 開發環境 URLs
- **Backend API**: http://localhost:8000
  - API 文檔: http://localhost:8000/docs
  - 健康檢查: http://localhost:8000/health
- **LineBot API**: http://localhost:5000
  - 健康檢查: http://localhost:5000/api/health
  - Debug 配置: http://localhost:5000/api/debug/config
- **Frontend**: http://localhost:4200
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Debug 端點
- **Backend Debug**: localhost:5678 (debugpy)
- **LineBot Debug**: localhost:5679 (debugpy)

## 🚀 VS Code Tasks

VS Code 內建了以下 tasks，可通過 `Ctrl+Shift+P` > `Tasks: Run Task` 執行：

- **Start All Debug Containers** - 啟動所有容器
- **Start Backend Debug Container** - 僅啟動 Backend 相關容器
- **Start LineBot Debug Container** - 啟動 LineBot 相關容器
- **Stop Debug Containers** - 停止所有容器
- **Restart Debug Containers** - 重啟所有容器
- **Show Debug URLs** - 顯示所有服務 URL
- **View Debug Logs** - 查看容器日誌
- **Clean Debug Environment** - 清理環境（包含資料卷）

## 🐛 調試工作流程

### 1. 設定斷點
在 VS Code 中直接在 Python 代碼行號左側點擊設定斷點

### 2. 啟動容器
```bash
# 啟動所有服務
docker-compose -f docker-compose_debug.yml up -d

# 檢查容器狀態
docker-compose -f docker-compose_debug.yml ps
```

### 3. 連接調試器
1. 在 VS Code Debug Panel 中選擇配置
2. 點擊 "Start Debugging" (F5)
3. 調試器會連接到容器中的 debugpy

### 4. 觸發斷點
- Backend: 發送 HTTP 請求到 http://localhost:8000
- LineBot: 發送請求到 http://localhost:5000

## 📝 常用命令

### Docker Compose 操作
```bash
# 啟動所有服務
docker-compose -f docker-compose_debug.yml up -d

# 查看日誌
docker-compose -f docker-compose_debug.yml logs -f

# 停止服務
docker-compose -f docker-compose_debug.yml down

# 重新建置並啟動
docker-compose -f docker-compose_debug.yml up -d --build

# 清理環境
docker-compose -f docker-compose_debug.yml down -v --remove-orphans
```

### 進入容器
```bash
# 進入 Backend 容器
docker exec -it smarthome_backend_debug bash

# 進入 LineBot 容器
docker exec -it smarthome_linebot_debug bash

# 進入資料庫容器
docker exec -it smarthome_db_debug psql -U postgres -d smarthome
```

## 🔍 疑難排解

### 1. 調試器無法連接
```bash
# 檢查容器是否正在運行
docker-compose -f docker-compose_debug.yml ps

# 檢查 debugpy 是否在等待連接
docker-compose -f docker-compose_debug.yml logs backend
docker-compose -f docker-compose_debug.yml logs linebot
```

### 2. 端口衝突
如果端口被佔用，修改 `docker-compose_debug.yml` 中的端口對應：
```yaml
ports:
  - "8001:8000"  # 改為其他端口
```

### 3. 代碼變更未生效
```bash
# 重啟容器以載入最新代碼
docker-compose -f docker-compose_debug.yml restart backend linebot
```

### 4. 資料庫連接問題
```bash
# 檢查資料庫健康狀態
docker-compose -f docker-compose_debug.yml exec db pg_isready -U postgres

# 查看資料庫日誌
docker-compose -f docker-compose_debug.yml logs db
```

## 💡 開發提示

### 1. 熱重載
- Backend (FastAPI): 使用 `--reload` 標誌，代碼變更會自動重載
- LineBot (Flask): 使用 `debug=True`，代碼變更會自動重載

### 2. 環境變數管理
- 使用 `.env.debug` 文件管理開發環境變數
- 生產環境使用不同的環境變數文件

### 3. 日誌查看
```bash
# 實時查看所有服務日誌
docker-compose -f docker-compose_debug.yml logs -f

# 查看特定服務日誌
docker-compose -f docker-compose_debug.yml logs -f backend
```

### 4. 效能監控
- 使用 VS Code 的 integrated terminal 監控資源使用
- 使用 `docker stats` 查看容器資源使用情況

## 📚 相關文檔

- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [Docker Compose](https://docs.docker.com/compose/)
- [debugpy Documentation](https://github.com/microsoft/debugpy/)
- [FastAPI Development](https://fastapi.tiangolo.com/tutorial/debugging/)
- [Flask Debugging](https://flask.palletsprojects.com/en/2.3.x/debugging/)

## 🎉 開始開發！

環境設定完成後，您可以：
1. 設定斷點並開始調試
2. 修改代碼並觀察即時效果
3. 使用 VS Code 的完整 Python 開發功能
4. 測試 API 端點和整合功能

Happy Debugging! 🐛✨
