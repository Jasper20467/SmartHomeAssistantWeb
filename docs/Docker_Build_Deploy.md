# Docker 建置與部署

## 服務清單

| 服務 | 映像 / Dockerfile | 應用端口 | Debug 端口 |
|------|------------------|---------|-----------|
| Backend (FastAPI) | `docker/backend.Dockerfile` | 8000 | 5678 |
| LineBotAI (Flask) | `docker/linebot.Dockerfile` | 5000 | 5679 |
| Frontend (Angular) | `docker/frontend.Dockerfile` | 4200 | — |
| PostgreSQL | `docker/postgres.Dockerfile` | 5432 | — |

---

## Debug 環境（本機開發）

使用 `docker-compose.yml`。原始碼以 volume mount 掛載，支援熱重載與 VS Code debugpy。

### 啟動

```bash
docker-compose up -d
```

### 服務端點

| 服務 | URL |
|------|-----|
| Frontend | http://localhost:4200 |
| Backend API | http://localhost:8000 |
| Backend API 文件 | http://localhost:8000/docs |
| Backend 健康檢查 | http://localhost:8000/health |
| LineBot | http://localhost:5000 |
| LineBot 健康檢查 | http://localhost:5000/api/health |
| PostgreSQL | localhost:5432 |

### VS Code Remote Debug 設定

```json
// .vscode/launch.json
{
  "configurations": [
    {
      "name": "Backend API Debug (Docker)",
      "type": "debugpy",
      "request": "attach",
      "connect": { "host": "localhost", "port": 5678 },
      "pathMappings": [
        { "localRoot": "${workspaceFolder}/backend", "remoteRoot": "/app" }
      ]
    },
    {
      "name": "LineBot API Debug (Docker)",
      "type": "debugpy",
      "request": "attach",
      "connect": { "host": "localhost", "port": 5679 },
      "pathMappings": [
        { "localRoot": "${workspaceFolder}/LineBotAI", "remoteRoot": "/app" }
      ]
    }
  ]
}
```

### 常用指令

```bash
# 查看服務狀態
docker-compose ps

# 查看即時日誌
docker-compose logs -f backend
docker-compose logs -f linebot

# 重建特定服務
docker-compose up -d --build backend

# 進入容器
docker exec -it smarthome_backend_debug bash

# 停止所有服務
docker-compose down

# 清理環境（含資料卷）
docker-compose down -v --remove-orphans
```

### VS Code Tasks

`Ctrl+Shift+P` → `Tasks: Run Task`：

| Task | 說明 |
|------|------|
| Start All Debug Containers | 啟動所有容器 |
| Start Backend Debug Container | 僅啟動 Backend + DB |
| Start LineBot Debug Container | 啟動 LineBot + Backend + DB |
| Stop Debug Containers | 停止所有容器 |
| Restart Debug Containers | 重啟所有容器 |
| Clean Debug Environment | 清理環境（含資料卷） |

---

## 環境變數

### Debug 環境（`.env`）

```env
# Backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/smarthome
ENVIRONMENT=development

# LineBot
BACKEND_API_URL=http://backend:8000
DEBUG_MODE=true
DEBUG_STAGE=true
LINE_CHANNEL_ACCESS_TOKEN=your_token
CHATGPT_API_KEY=your_key
```

### 生產環境

```env
# Backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/smarthome
ENVIRONMENT=production

# LineBot
DOMAIN_NAME=smarthome.the-jasperezlife.com
DEBUG_MODE=false
DEBUG_STAGE=false
LINE_CHANNEL_ACCESS_TOKEN=your_token
CHATGPT_API_KEY=your_key
```

---

## 時區設定

所有 Dockerfile 已內建時區設定，**不需要**掛載主機時區檔案。

```dockerfile
# Alpine 基礎（Frontend）
RUN apk add --no-cache tzdata
ENV TZ=Asia/Taipei
RUN cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && echo "Asia/Taipei" > /etc/timezone

# Python 基礎（Backend / LineBot）
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```

Docker Compose 中另設環境變數確保一致性：

```yaml
environment:
  - TZ=Asia/Taipei
  # PostgreSQL 額外需要：
  - PGTZ=Asia/Taipei
```

> **避免**掛載 `/etc/timezone` 或 `/etc/localtime`。在某些 Linux 主機（如 AWS EC2）上這些檔案不存在，會導致容器啟動失敗。

---

## 推送映像至 Docker Hub

使用 `scripts/quick_push.ps1`：

```powershell
# 使用自動生成的時間戳版本號（例如 2025.07.06.1200）
.\scripts\quick_push.ps1

# 指定版本號
.\scripts\quick_push.ps1 1.2
```

### 映像名稱

| 服務 | 映像 |
|------|------|
| Frontend | `popo510691/homeassistant.frontend` |
| Backend | `popo510691/homeassistant.backend` |
| LineBot | `popo510691/homeassistant.linebot` |

每次推送同時建立指定版本標籤與 `latest` 標籤。

### 前置需求

```powershell
docker login
```

---

## 生產部署（AWS EC2 + Docker Compose）

```bash
cd scripts/DeployOn_AWS_Ec2
docker-compose -f docker-compose_fromHub.yml pull
docker-compose -f docker-compose_fromHub.yml up -d
```

### 反向代理（Caddy）

```caddy
# API 路由
@api {
  path /api/*
}
reverse_proxy @api backend:8000

# LineBot 路由
@linebot {
  path /webhook
  path /linebot/*
  path /api/debug/*
}
reverse_proxy @linebot linebot:5000
```

---

## 故障排除

### Backend 無法連接資料庫
- 確認 `DATABASE_URL` 使用 `postgresql+asyncpg://`
- 確認 PostgreSQL 容器已啟動且健康檢查通過

### Frontend 無法存取 Backend API
- 確認所有服務都在同一個 Docker network（`app-network`）
- 確認 Nginx 設定正確代理到 `backend:8000`

### LineBot 無法連接 Backend
- 確認 `BACKEND_API_URL` 或 `DEBUG_MODE` + `DOMAIN_NAME` 設定正確
- 使用 `curl http://localhost:5000/api/debug/backend` 測試

### 映像推送失敗
```powershell
# 重新登入
docker logout
docker login

# 查看詳細建置日誌
docker build --progress=plain -f docker/backend.Dockerfile ./backend
```
