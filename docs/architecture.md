# 系統架構圖 — 家用智慧助理系統

---

## 整體架構概覽

> 以下為**生產環境（AWS EC2）**架構。本地開發使用 `docker-compose.yml`，各服務端口直接對外，不經過 Caddy。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           使用者端 (Clients)                             │
│                                                                         │
│   ┌──────────────────┐              ┌──────────────────────────────┐   │
│   │   Web 瀏覽器      │              │        LINE App              │   │
│   │  (家庭成員)       │              │       (家庭成員)              │   │
│   └────────┬─────────┘              └──────────────┬───────────────┘   │
└────────────┼──────────────────────────────────────┼────────────────────┘
             │ HTTPS                                 │ LINE Messaging API
             │                                       │ (POST /webhook)
             ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AWS Route 53                                                           │
│  smarthome.the-jasperezlife.com  →  EC2 Elastic IP                      │
└─────────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AWS EC2 Instance (Ubuntu, TZ=Asia/Taipei)                              │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Caddy 2  (edge proxy)  :80 / :443                               │  │
│  │                                                                   │  │
│  │  ● 自動申請 & 續約 Let's Encrypt TLS 憑證                          │  │
│  │  ● zstd / gzip 壓縮                                               │  │
│  │  ● 安全性 HTTP 標頭（HSTS、CSP、X-Frame-Options...）               │  │
│  │                                                                   │  │
│  │  路由規則:                                                         │  │
│  │  /webhook, /linebot/*, /api/debug/*  →  linebot:5000             │  │
│  │  /api/*                              →  backend:8000             │  │
│  │  (其餘)                              →  frontend:80              │  │
│  └───────┬──────────────────┬──────────────────┬─────────────────────┘  │
│          │                  │                  │                        │
│          ▼                  ▼                  ▼                        │
└─────────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Docker 應用網路 (app-network)                    │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              frontend  (Nginx + Angular SPA)  :80                │  │
│  │                                                                  │  │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │  │
│  │   │  /dashboard  │  │  /schedule   │  │    /consumable       │  │  │
│  │   │ DashboardComp│  │ ScheduleComp │  │   ConsumableComp     │  │  │
│  │   └──────────────┘  └──────────────┘  └──────────────────────┘  │  │
│  │                                                                  │  │
│  │   ┌──────────────────────────────────────────────────────────┐  │  │
│  │   │              共用元件 (Header / Sidebar / Calendar)       │  │  │
│  │   └──────────────────────────────────────────────────────────┘  │  │
│  │                                                                  │  │
│  │   Nginx 反向代理:  location /api/ → proxy_pass backend:8000     │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │ /api/* (HTTP proxy)               │
│                                     ▼                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              backend  (FastAPI + Uvicorn)  :8000                 │  │
│  │                                                                  │  │
│  │   ┌─────────────────────────┐  ┌────────────────────────────┐   │  │
│  │   │   /api/schedules/*      │  │   /api/consumables/*       │   │  │
│  │   │  GET / POST / PUT       │  │  GET / POST / PUT          │   │  │
│  │   │  DELETE / by-date/{d}   │  │  DELETE                    │   │  │
│  │   └────────────┬────────────┘  └────────────┬───────────────┘   │  │
│  │                │                             │                   │  │
│  │   ┌────────────▼─────────────────────────────▼────────────────┐ │  │
│  │   │          SQLAlchemy 2.0 Async ORM (AsyncPG)               │ │  │
│  │   └──────────────────────────────┬────────────────────────────┘ │  │
│  └─────────────────────────────────┼────────────────────────────────┘  │
│                                    │ asyncpg                            │
│                                    ▼                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              db  (PostgreSQL 14)  :5432                          │  │
│  │                                                                  │  │
│  │   ┌────────────────────────────┐  ┌───────────────────────────┐ │  │
│  │   │  schedules                 │  │  consumables              │ │  │
│  │   │  ─ id (PK)                 │  │  ─ id (PK)                │ │  │
│  │   │  ─ title                   │  │  ─ name                   │ │  │
│  │   │  ─ description             │  │  ─ category               │ │  │
│  │   │  ─ start_time (TIMESTAMPTZ)│  │  ─ installation_date      │ │  │
│  │   │  ─ end_time   (TIMESTAMPTZ)│  │  ─ lifetime_days          │ │  │
│  │   │  ─ created_at / updated_at │  │  ─ notes                  │ │  │
│  │   └────────────────────────────┘  │  ─ created_at / updated_at│ │  │
│  │                                   └───────────────────────────┘ │  │
│  │   Volume: postgres_data (persistent)                             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              linebot  (Flask + LangGraph)  :5000                 │  │
│  │                                                                  │  │
│  │   POST /webhook                                                  │  │
│  │        │                                                         │  │
│  │        ▼                                                         │  │
│  │   LineService.process_user_message()                             │  │
│  │        │                                                         │  │
│  │        ▼                                                         │  │
│  │   AgentService.run(user_message, user_id)                        │  │
│  │   ┌─────────────────────────────────────────────────────────┐   │  │
│  │   │         LangGraph ReAct Agent                           │   │  │
│  │   │                                                         │   │  │
│  │   │   ┌─────────────────────────────────────────────┐      │   │  │
│  │   │   │  Google Gemini 2.0 Flash (LLM)              │      │   │  │
│  │   │   │  - 繁體中文回應                              │      │   │  │
│  │   │   │  - 動態注入台灣時間 (UTC+8)                  │      │   │  │
│  │   │   │  - ReAct 推理鏈 (Reason → Act → Observe)    │      │   │  │
│  │   │   └─────────────────────────────────────────────┘      │   │  │
│  │   │                                                         │   │  │
│  │   │   ┌─────────────────────────────────────────────┐      │   │  │
│  │   │   │  8 個 LangChain Tools                        │      │   │  │
│  │   │   │  ─ get/create/update/delete_schedule         │      │   │  │
│  │   │   │  ─ get/create/update/delete_consumable       │      │   │  │
│  │   │   └──────────────────┬──────────────────────────┘      │   │  │
│  │   │                      │ HTTP                             │   │  │
│  │   │                      ▼                                  │   │  │
│  │   │   HomeAssistantClient → backend:8000/api/*              │   │  │
│  │   │                                                         │   │  │
│  │   │   ┌─────────────────────────────────────────────┐      │   │  │
│  │   │   │  MemorySaver (In-Memory 對話記憶體)           │      │   │  │
│  │   │   │  thread_id = f"{user_id}:{version}"          │      │   │  │
│  │   │   │  TTL: 24 小時 / Max Messages: 30             │      │   │  │
│  │   │   └─────────────────────────────────────────────┘      │   │  │
│  │   └─────────────────────────────────────────────────────────┘   │  │
│  │        │                                                         │  │
│  │        ▼                                                         │  │
│  │   reply_to_line(reply_token, message)                            │  │
│  └──────────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  │ HTTPS
                                  ▼
                    ┌─────────────────────────────┐
                    │  LINE Messaging API          │
                    │  api.line.me/v2/bot/message/ │
                    │  reply                       │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                              LINE App 用戶
```

---

## LINE Bot 對話流程

```
LINE 用戶傳訊
      │
      ▼
LINE Messaging API
      │  POST /webhook
      ▼
Flask LineBot App (:5000)
      │
      ▼
LineService.process_user_message(user_message, reply_token, user_id)
      │
      ├─► AgentService.run(user_message, user_id)
      │         │
      │         ├─ 檢查 Memory TTL (>24h → clear + version bump)
      │         ├─ 訊息數量限制 (>30 → 修剪舊訊息)
      │         │
      │         ▼
      │   LangGraph ReAct 迴圈:
      │   ┌──────────────────────────────────────────────────────┐
      │   │  1. Reason: Gemini 分析用戶意圖                       │
      │   │  2. Act:    選擇並呼叫適當工具 (Tool Call)             │
      │   │     └─► HomeAssistantClient → backend:8000/api/*     │
      │   │  3. Observe: 接收工具執行結果                          │
      │   │  4. 判斷是否需要繼續推理或生成最終回應                   │
      │   └──────────────────────────────────────────────────────┘
      │         │
      │         ▼
      │   回傳 agent_reply (繁體中文)
      │
      ▼
reply_to_line(reply_token, agent_reply)
      │  POST api.line.me/v2/bot/message/reply
      ▼
LINE 用戶收到回覆
```

---

## Web 前端請求流程

### 生產環境（EC2 + Caddy）

```
瀏覽器 (HTTPS)
      │
      ▼
Caddy (:443)  ← TLS 終止、安全標頭注入
      │
      ├── /api/*  →  backend:8000 (FastAPI)
      │                   │ SQLAlchemy Async
      │                   ▼ PostgreSQL (:5432)
      │
      └── (其餘) →  frontend:80 (Nginx)
                         │ 靜態資源 / Angular SPA
                         │ try_files → index.html
                         ▼
                    Angular Router → 渲染頁面
```

### 本地開發（Docker Compose，無 Caddy）

```
瀏覽器 (HTTP)
      │
      ▼
Nginx frontend:80
      │
      ├── /api/*  →  proxy_pass backend:8000 (FastAPI)
      │                   │ SQLAlchemy Async
      │                   ▼ PostgreSQL (:5432)
      │
      └── (其餘) →  Angular SPA (index.html)
```

---

## 元件相依關係

```
frontend ──────────────────────────────► backend
                                              │
linebot ──► HomeAssistantClient ──────────────┘
   │
   └──► LINE Messaging API (外部)
   └──► Google Gemini API  (外部)

backend ──► PostgreSQL (db)
```

---

## 資料庫 Schema

```
┌──────────────────────────────────┐    ┌──────────────────────────────────┐
│           schedules              │    │          consumables             │
├──────────────────────────────────┤    ├──────────────────────────────────┤
│ id           SERIAL PK           │    │ id           SERIAL PK           │
│ title        VARCHAR(255) NOT NULL│    │ name         VARCHAR(255) NOT NULL│
│ description  TEXT                │    │ category     VARCHAR(100) NOT NULL│
│ start_time   TIMESTAMPTZ NOT NULL │    │ installation_date  DATE NOT NULL  │
│ end_time     TIMESTAMPTZ         │    │ lifetime_days  INTEGER NOT NULL   │
│ created_at   TIMESTAMPTZ DEFAULT │    │ notes        TEXT                │
│ updated_at   TIMESTAMPTZ DEFAULT │    │ created_at   TIMESTAMPTZ DEFAULT │
└──────────────────────────────────┘    │ updated_at   TIMESTAMPTZ DEFAULT │
                                        │ [virtual]                        │
                                        │ days_remaining (計算欄位)         │
                                        └──────────────────────────────────┘
```

---

## 部署架構

### 本地開發 (Docker Compose)

```
localhost
├── :80   → frontend  (Nginx + Angular)
├── :8000 → backend   (FastAPI)
├── :5000 → linebot   (Flask)
├── :5432 → db        (PostgreSQL)
├── :5678 → backend   (debugpy)
└── :5679 → linebot   (debugpy)

網路: app-network (Docker Bridge)
磁碟: postgres_data (Named Volume)
```

### 本地開發 (docker-compose.yml)

```
localhost
├── :80   → frontend  (Nginx + Angular，從原始碼建置)
├── :8000 → backend   (FastAPI，熱重載)
├── :5000 → linebot   (Flask，熱重載)
├── :5432 → db        (PostgreSQL)
├── :5678 → backend   (debugpy)
└── :5679 → linebot   (debugpy)

網路: app-network (Docker Bridge)
磁碟: postgres_data (Named Volume)
```

### 生產環境 (docker-compose_fromHub.yml + Caddy)

```
Internet (HTTPS :443 / HTTP :80)
    │
    ▼
AWS Route 53
    smarthome.the-jasperezlife.com → EC2 Elastic IP
    │
    ▼
AWS EC2 Instance (Ubuntu, TZ=Asia/Taipei)
    │
    └── Docker Compose (docker-compose_fromHub.yml)
        │
        ├── caddy     (Caddy 2 :80/:443)          ← 唯一對外端口
        │       自動 Let's Encrypt TLS
        │       路由: /webhook,/linebot/* → linebot:5000
        │             /api/*             → backend:8000
        │             (其餘)             → frontend:80
        │
        ├── frontend  (Nginx + Angular，expose :80)
        ├── backend   (FastAPI，expose :8000)
        ├── linebot   (Flask，expose :5000)
        └── db        (PostgreSQL，port :5432)

網路: app-network (Docker Bridge)
磁碟: postgres_data / caddy_data / caddy_config (Named Volumes)

映像來源: Docker Hub (Public)
    popo510691/homeassistant.frontend:latest
    popo510691/homeassistant.backend:latest
    popo510691/homeassistant.linebot:latest
```

#### CI/CD 部署流程

```
開發者 push to main
    │
    ▼
GitHub Actions
    ├── docker build (frontend / backend / linebot)
    ├── docker push  → Docker Hub (Public)
    └── SSH → EC2
                └── docker-compose -f docker-compose_fromHub.yml pull
                    docker-compose -f docker-compose_fromHub.yml up -d --force-recreate
```

---

## 外部服務整合

| 服務 | 用途 | 認證方式 |
|------|------|---------|
| LINE Messaging API | 接收/傳送 LINE 訊息 | `LINE_CHANNEL_ACCESS_TOKEN` (Bearer) |
| Google Gemini API | LLM 推理引擎 | `GEMINI_API_KEY` |
| Let's Encrypt (ACME) | TLS 憑證自動申請與續約（由 Caddy 處理） | ACME HTTP-01 Challenge |
| Docker Hub (Public) | 容器映像倉庫 | `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` |
| AWS EC2 | 生產環境運算主機 | SSH Key Pair |
| AWS Route 53 | DNS 管理（A Record → EC2 Elastic IP） | AWS IAM |

---

## Caddyfile 設計說明

Caddy 是生產環境的唯一對外入口，部署於 `docker-compose_fromHub.yml`，設定檔為專案根目錄的 `Caddyfile`。

### 路由優先順序

Caddy 依 matcher 由上至下匹配，第一個命中的規則生效：

```
1. @linebot  →  path /webhook, /linebot/*, /api/debug/*  →  linebot:5000
2. @api      →  path /api/*                              →  backend:8000
3. (預設)    →  其餘所有路徑                              →  frontend:80
```

### TLS 自動管理

Caddy 在首次啟動時透過 ACME HTTP-01 Challenge 向 Let's Encrypt 申請憑證，並在到期前自動續約。憑證儲存於 `caddy_data` Docker Volume（持久化），重啟不會遺失。

測試部署時可在 Caddyfile 全域區塊加入：
```
acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
```
改用 staging CA 避免觸及 Let's Encrypt 正式環境的 rate limit（每週 5 張/domain）。

### 安全性標頭

| 標頭 | 設定值 | 目的 |
|------|--------|------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | 強制 HTTPS，防止降級攻擊 |
| `X-Content-Type-Options` | `nosniff` | 防止 MIME 類型嗅探 |
| `X-Frame-Options` | `DENY` | 防止 Clickjacking |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | 控制 Referrer 洩漏範圍 |
| `Content-Security-Policy` | `default-src 'self'; ...` | 限制資源載入來源 |
| `Access-Control-Allow-Origin` | `*` | LINE Webhook 跨域需求 |

### Volume 說明

| Volume | 用途 |
|--------|------|
| `caddy_data` | TLS 憑證與 ACME 帳號（持久化，重啟不失效） |
| `caddy_config` | Caddy 執行時自動產生的設定快取 |
| `Caddyfile` (bind mount) | 以唯讀掛載專案根目錄的 Caddyfile |

---

## 時區架構

```
所有容器: TZ=Asia/Taipei (UTC+8)
    │
    ├── PostgreSQL: PGTZ=Asia/Taipei + TIMESTAMP WITH TIME ZONE
    ├── Backend: tzinfo aware datetime (Python)
    ├── LineBotAI: System Prompt 動態注入當前台灣時間
    └── Frontend: ISO 8601 (+08:00) 格式顯示

API 時間格式: "2025-01-01T10:00:00+08:00" (ISO 8601 with offset)
```

---

## AI Agent 記憶體架構

```
用戶 A (user_id: "U123")                用戶 B (user_id: "U456")
    │                                        │
    ▼                                        ▼
thread_id: "U123:1"                   thread_id: "U456:1"
    │                                        │
    ▼                                        ▼
┌─────────────────────┐            ┌─────────────────────┐
│  LangGraph          │            │  LangGraph          │
│  MemorySaver        │            │  MemorySaver        │
│  (In-Memory)        │            │  (In-Memory)        │
│  Max: 30 messages   │            │  Max: 30 messages   │
│  TTL: 24 hours      │            │  TTL: 24 hours      │
└─────────────────────┘            └─────────────────────┘

TTL 過期 → version+1 → thread_id: "U123:2" (新對話)
錯誤復原 → clear + retry (同 version)
```
