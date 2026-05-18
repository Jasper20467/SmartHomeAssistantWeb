# 家用智慧助理系統 (Smart Home Assistant)

一個全功能的智能家庭管理平台，幫助家庭成員管理日常行程、追蹤家用耗材更換週期，並透過 LINE Bot AI 助理進行自然語言互動。

---

## 功能特點

- **家庭行事曆**: 集中管理全家人的行程與活動，支援依日期查詢
- **耗材管理**: 智能追蹤家用耗材（如濾水器、空氣清淨機濾網）的更換週期，自動計算剩餘天數
- **LINE Bot AI 助理**: 透過 LINE 以自然語言新增、查詢、修改行程與耗材記錄（LangGraph ReAct Agent + Google Gemini）
- **多用戶對話隔離**: 每位 LINE 用戶擁有獨立的 AI 對話記憶體
- **智能裝置控制**: 整合多種智能家電，實現集中管理 (TBD)
- **能源監控**: 追蹤家庭能源使用情況，提供節能建議 (TBD)

---

## 技術堆疊

| 層級 | 技術 |
|------|------|
| 前端 | Angular 17 + TypeScript + RxJS |
| 後端 | FastAPI (Python 3.10) + SQLAlchemy 2.0 Async |
| 資料庫 | PostgreSQL 14 (生產) / SQLite (開發 Demo) |
| AI Agent | LangGraph ReAct Agent + Google Gemini 2.0 Flash |
| 即時通訊 | LINE Messaging API + Flask |
| 容器化 | Docker & Docker Compose |
| Edge Proxy | Caddy 2（自動 HTTPS / TLS、反向代理） |
| 雲端部署 | AWS EC2 + Route 53 |
| CI/CD | GitHub Actions |

---

## 專案結構

```
SmartHomeAssistantWeb/
├── frontend/                    # Angular 17 SPA 前端
│   └── src/app/
│       ├── pages/               # 頁面元件 (dashboard, schedule, consumable)
│       ├── shared/
│       │   ├── components/      # 共用元件 (header, sidebar, calendar)
│       │   ├── models/          # 資料模型 (schedule, consumable)
│       │   └── services/        # HTTP 服務
│       └── environments/        # 環境配置
├── backend/                     # FastAPI REST API 後端
│   └── app/
│       ├── api/                 # API 路由 (schedules, consumables)
│       ├── models/              # SQLAlchemy ORM 模型
│       ├── database/            # 資料庫初始化與連線
│       └── main.py              # 應用程式進入點
├── LineBotAI/                   # LINE Bot + LangGraph AI Agent
│   ├── agent/                   # Agent 工具與 Prompt 定義
│   ├── services/                # LINE 訊息處理 & Agent 服務
│   ├── Home_assistant/          # 後端 API 客戶端
│   ├── config/                  # 環境配置
│   ├── tests/                   # 單元測試
│   └── app.py                   # Flask 進入點 (Webhook)
├── docker/                      # Dockerfile & Nginx 配置
├── scripts/
│   └── DeployOn_AWS_Ec2/        # AWS EC2 部署腳本
├── docker-compose.yml           # 本地開發（從原始碼建置）
├── docker-compose_fromHub.yml   # 生產環境（從 Docker Hub pull image）
├── Caddyfile                    # Caddy edge proxy 設定（HTTPS / 路由）
└── .env.example                 # 環境變數範本
```

---

## 安裝與設置

### 前置需求

- Docker & Docker Compose
- Node.js 18+ (本地前端開發用)
- Python 3.10+ (本地後端/LineBotAI 開發用)

### 快速啟動 (本地開發)

```bash
# 克隆專案
git clone https://github.com/yourusername/SmartHomeAssistantWeb.git
cd SmartHomeAssistantWeb

# 複製並設定環境變數
cp .env.example .env
# 編輯 .env，填入 LINE_CHANNEL_ACCESS_TOKEN 和 GEMINI_API_KEY

# 從原始碼建置並啟動（不含 Caddy，各服務端口直接對外）
docker-compose up --build
```

啟動後訪問:
- **前端 Web**: http://localhost:80
- **後端 API**: http://localhost:8000
- **LineBotAI**: http://localhost:5000
- **API 文件**: http://localhost:8000/docs

### VS Code Debug 環境

支援 VS Code Remote Debugging（含熱重載）：

```bash
docker-compose up -d
```

1. 打開 VS Code Debug Panel (`Ctrl+Shift+D`)
2. 選擇 "Backend API Debug (Docker)" 或 "LineBot API Debug (Docker)"
3. 點擊 F5 開始調試

Debug 端口: Backend `5678` / LineBot `5679`

### 本地直接安裝

```bash
# 前端
cd frontend && npm install && ng serve

# 後端 (另開終端)
cd backend
python -m venv venv && venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# LineBotAI (另開終端)
cd LineBotAI
pip install -r requirements.txt
python app.py
```

---

## 環境變數

複製 `.env.example` 為 `.env` 並設定以下必要項目：

```env
# 資料庫
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=smarthome
DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome

# LINE Bot
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash

# LineBotAI
BACKEND_API_URL=http://backend:8000
DEBUG_MODE=false
AGENT_MEMORY_TTL_SECONDS=86400
AGENT_MAX_MESSAGES=30
```

---

## API 端點

### 後端 (FastAPI)

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/schedules/` | 取得所有行程（支援分頁） |
| POST | `/api/schedules/` | 新增行程 |
| GET | `/api/schedules/{id}` | 取得單一行程 |
| PUT | `/api/schedules/{id}` | 更新行程 |
| DELETE | `/api/schedules/{id}` | 刪除行程 |
| GET | `/api/schedules/by-date/{date}` | 依日期查詢行程 |
| GET | `/api/consumables/` | 取得所有耗材（含剩餘天數） |
| POST | `/api/consumables/` | 新增耗材 |
| GET | `/api/consumables/{id}` | 取得單一耗材 |
| PUT | `/api/consumables/{id}` | 更新耗材 |
| DELETE | `/api/consumables/{id}` | 刪除耗材 |

### LineBotAI (Flask)

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/webhook` | LINE Messaging API Webhook |
| GET | `/api/health` | 健康檢查 |
| GET | `/linebot/health` | LineBotAI 健康檢查（含後端 URL 資訊） |
| POST | `/api/debug/chat` | Debug 對話測試（需 `DEBUG_STAGE=true`） |

---

## AI Agent 工具

LineBotAI 的 LangGraph ReAct Agent 配備 8 個工具，可操作後端 API：

| 工具 | 功能 |
|------|------|
| `get_schedules` | 查詢行程（可依日期過濾） |
| `create_schedule` | 新增行程（ISO 8601 時間格式） |
| `update_schedule` | 更新行程 |
| `delete_schedule` | 刪除行程 |
| `get_consumables` | 查詢所有耗材（含剩餘天數） |
| `create_consumable` | 新增耗材追蹤 |
| `update_consumable` | 更新耗材資訊 |
| `delete_consumable` | 刪除耗材 |

Agent 特性：
- 每位 LINE 用戶擁有獨立對話線程（`thread_id`）
- 對話記憶體 TTL（預設 24 小時）過期後自動清除
- 訊息數量限制（`AGENT_MAX_MESSAGES`），避免 token 超用
- 自動復原損壞的對話歷史
- System Prompt 動態注入台灣時間（UTC+8），確保時間操作正確

---

## 部署

### 重要：時區設定

所有容器已設定 `TZ=Asia/Taipei`，確保行程時間戳記一致。

```bash
# 確認 EC2 時區設定
sudo timedatectl set-timezone Asia/Taipei
timedatectl status
```

### AWS EC2 部署

生產環境部署於 AWS EC2，DNS 由 AWS Route 53 管理。Caddy 作為 edge proxy 負責自動申請 Let's Encrypt TLS 憑證、HTTPS 終止與路由分流。Docker Image 推送至 Public Docker Hub，EC2 從 Docker Hub pull image 後以 `docker-compose_fromHub.yml` 啟動。

#### 服務流量分流（Caddyfile）

| 路徑 | 轉發目標 |
|------|---------|
| `/webhook`, `/linebot/*`, `/api/debug/*` | linebot:5000 |
| `/api/*` | backend:8000 |
| 其餘所有路徑 | frontend:80（Nginx + Angular SPA）|

#### 部署流程

```bash
# 1. 本地建置並推送 Image 到 Docker Hub
docker build -f ./docker/frontend.Dockerfile -t popo510691/homeassistant.frontend:latest ./frontend
docker build -f ./docker/backend.Dockerfile  -t popo510691/homeassistant.backend:latest ./backend
docker build -f ./docker/linebot.Dockerfile  -t popo510691/homeassistant.linebot:latest .
docker push popo510691/homeassistant.frontend:latest
docker push popo510691/homeassistant.backend:latest
docker push popo510691/homeassistant.linebot:latest

# 2. SSH 進入 EC2
# 確認時區設定
sudo timedatectl set-timezone Asia/Taipei

# 複製 .env 並填入 secrets（首次部署）
cp .env.example .env

# 從 Docker Hub 拉取最新 Image 並啟動（含 Caddy）
docker-compose -f docker-compose_fromHub.yml pull
docker-compose -f docker-compose_fromHub.yml up -d --force-recreate
```

Caddy 會在首次啟動時自動向 Let's Encrypt 申請憑證，憑證資料儲存於 `caddy_data` volume 並自動續約。

#### Route 53 DNS 設定

| 記錄類型 | 名稱 | 指向 |
|---------|------|------|
| A | `smarthome.the-jasperezlife.com` | EC2 Elastic IP |

---

## CI/CD

GitHub Actions 自動化工作流程（推送至 `main` 分支或建立 `v*.*.*` 標籤時觸發）：

1. 建置 Docker Image
2. 推送至 Public Docker Hub
3. SSH 進入 EC2 執行 `docker-compose pull && docker-compose up -d`

所需 GitHub Secrets：
- `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN`
- `EC2_HOST`、`EC2_SSH_KEY`
- `DB_PASSWORD`

---

## 故障排除

### Angular 路由 404 問題

Nginx 已配置 `try_files $uri $uri/ /index.html`，所有路由均回退至 `index.html`。

### CORS 問題

後端已允許以下來源：
- `http://localhost:4200`（Angular 開發）
- `http://localhost`（Docker 前端）
- `https://smarthome.the-jasperezlife.com`（生產環境）

### 資料庫連線問題

後端啟動時具備指數退避重試機制（最多 5 次）。若連線持續失敗：

```bash
docker-compose ps          # 確認 db 容器狀態
docker-compose down && docker-compose up --build
```

---

## 分支策略

- `main`: 生產環境分支
- `develop`: 開發分支
- `feature/*`: 功能分支
- `hotfix/*`: 緊急修復分支

---

## 授權

MIT License

---

## 聯絡資訊

- **問題回報**: [Issue Tracker](https://github.com/yourusername/SmartHomeAssistantWeb/issues)
