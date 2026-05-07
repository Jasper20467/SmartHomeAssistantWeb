# Copilot Instructions — Smart Home Assistant Web

## 專案概覽

「家用智慧助理系統」是一個多服務智慧家庭管理平台，由三個獨立服務組成：

| 服務 | 技術 | 說明 |
|------|------|------|
| **Frontend** | Angular 17 + TypeScript | SPA 管理介面 |
| **Backend** | FastAPI + SQLAlchemy (async) | REST API 服務 |
| **LineBotAI** | Flask + OpenAI GPT | LINE 聊天機器人 |

資料庫：PostgreSQL（生產 / Debug 環境）、SQLite（Demo 環境）

---

## 系統架構

```
User (Browser)
    └── Angular 17 SPA (port 4200)
            └── HTTP → Backend FastAPI (port 8000)
                        └── asyncpg → PostgreSQL (port 5432)

LINE User
    └── Webhook → LineBotAI Flask (port 5000)
                    ├── OpenAI API (gpt-4.1-nano)
                    └── HTTP → Backend FastAPI (port 8000)
```

### 資料流（LineBotAI）
```
LINE Webhook → LineService.process_user_message()
    → ChatGPTService.process_message()  # 回傳 action + parameters JSON
    → LineService._perform_backend_operation()
        → HomeAssistantClient → ScheduleService / ConsumableService
            → Backend REST API
    → LineService.reply_to_line()
```

---

## 各服務目錄結構

### Backend (`backend/`)
```
app/
├── main.py          # FastAPI app 建立、CORS、router 掛載
├── config.py        # 環境設定
├── api/             # 路由處理器（schedules.py、consumables.py）
├── database/
│   ├── database.py  # async engine、session、get_db dependency
│   └── init_db.py   # 建表邏輯
└── models/          # SQLAlchemy ORM 模型
```

### Frontend (`frontend/src/app/`)
```
pages/
├── dashboard/       # 儀表板
├── schedule/        # 行程管理
└── consumable/      # 耗材管理
shared/
├── models/          # TypeScript interface（schedule.model.ts、consumable.model.ts）
├── services/        # HttpClient 服務（schedule.service.ts、consumable.service.ts）
└── components/      # 共用元件（header、sidebar、calendar、loading-spinner）
environments/        # apiUrl 設定
```

### LineBotAI (`LineBotAI/`)
```
app.py               # Flask app factory，Webhook 入口
services/
├── line_service.py  # LINE 訊息收發 + 後端操作協調
├── chatgpt_service.py  # OpenAI API 呼叫 + 對話歷史管理
└── api_utils.py     # HomeAssistantClient 封裝工具
Home_assistant/      # 後端 API 客戶端套件
├── client.py        # HomeAssistantClient（整合所有 service）
├── base_service.py  # HTTP 請求基底
├── schedule_service.py
├── consumable_service.py
└── device_service.py
config/
└── url_config.py    # 動態取得 backend URL（依環境判斷）
```

---

## 開發規範

### Backend（Python / FastAPI）

- **非同步優先**：所有 DB 操作使用 `async/await` + `AsyncSession`；依賴注入使用 `Depends(get_db)`。
- **Pydantic v2**：Schema 類別直接放在對應的 router 檔案內（`Base` / `Create` / `Update` / `Response` 命名規則）；`Response` 類別設定 `orm_mode = True`（`Config` 內）。
- **Router 結構**：每個資源對應一個 `APIRouter`，在 `main.py` 以 `/api/{resource}` prefix 掛載。
- **命名**：Python snake_case；資料表名稱複數（`schedules`、`consumables`）。
- **時區**：所有 `DateTime` 欄位使用 `timezone=True`；程式內時間計算使用台灣時間（UTC+8）。
- **環境變數**：透過 `os.getenv()` 讀取，不寫死敏感資訊。預設值僅限 Docker 內部網路路徑（如 `db:5432`）。

### Frontend（TypeScript / Angular）

- **模組架構**：使用 `NgModule`（非 standalone components）；所有元件在 `AppModule` 宣告。
- **型別定義**：共用介面放在 `shared/models/`；Service 放在 `shared/services/`，以 `providedIn: 'root'` 注入。
- **HTTP 呼叫**：透過 Service 封裝，元件不直接使用 `HttpClient`；API URL 從 `environment.apiUrl` 讀取。
- **表單**：使用 `ReactiveFormsModule`（`FormBuilder` + `FormGroup`）。
- **命名**：TypeScript camelCase；Angular selector 前綴 `app-`。
- **樣式**：各元件有對應 `.scss` 檔；全域樣式在 `src/styles.scss`。

### LineBotAI（Python / Flask）

- **App Factory**：Flask app 以 `create_app()` 工廠函式建立。
- **服務職責分離**：`LineService` 處理 LINE 協定；`ChatGPTService` 處理 AI 邏輯；`HomeAssistantClient` 封裝所有後端呼叫。
- **ChatGPT 回應格式**：GPT 應回傳 JSON，包含 `action`、`parameters`、`reply` 欄位。`action` 值：`text_reply`、`create_schedule`、`get_schedule`、`update_schedule`、`delete_schedule`、`create_consumable`、`get_consumable`、`update_consumable`、`delete_consumable`。
- **對話歷史**：每位 LINE 用戶（`user_id`）維護獨立的 `deque`（最多 5 輪）。
- **Backend URL**：一律透過 `config/url_config.py` 的 `get_backend_url()` 取得，不直接讀取環境變數。

---

## 環境與部署

### Debug 環境（本機開發）

```bash
# 啟動所有容器（含 debugpy）
docker-compose up -d
```

| 服務 | 應用端口 | Debug 端口 |
|------|---------|-----------|
| Backend | 8000 | 5678 |
| LineBotAI | 5000 | 5679 |
| Frontend | 4200 | — |
| PostgreSQL | 5432 | — |

- 原始碼以 volume mount 掛載，支援熱重載。
- VS Code debugpy 設定檔位於 `.vscode/launch.json`。

### 重要環境變數

| 變數 | 使用服務 | 說明 |
|------|---------|------|
| `DATABASE_URL` | Backend | `postgresql+asyncpg://...` |
| `LINE_CHANNEL_ACCESS_TOKEN` | LineBotAI | LINE channel token |
| `CHATGPT_API_KEY` | LineBotAI | OpenAI API key |
| `BACKEND_API_URL` | LineBotAI | 覆寫預設後端 URL |
| `DEBUG_MODE` | LineBotAI | `true` 時使用容器內網路 |
| `DOMAIN_NAME` | LineBotAI | 生產環境網域名稱 |

### 生產環境

- 部署至 **Azure Container Apps**，配置於 `scripts/DeployOn_Azure_ContainerApps/`。
- IaC 使用 Bicep（`main.bicep`）。
- CI/CD 使用 Azure Pipelines（`github-workflow-template.yml`）。

---

## API 端點摘要

### Backend REST API（`/api/`）

**Schedules** (`/api/schedules/`)
- `GET /` — 取得所有行程（支援 `date_filter=YYYY-MM-DD` query param）
- `POST /` — 新增行程
- `GET /{id}` — 取得單筆
- `PUT /{id}` — 更新行程
- `DELETE /{id}` — 刪除行程

**Consumables** (`/api/consumables/`)
- `GET /` — 取得所有耗材（回應包含計算後的 `days_remaining`）
- `POST /` — 新增耗材
- `GET /{id}` — 取得單筆
- `PUT /{id}` — 更新耗材
- `DELETE /{id}` — 刪除耗材

---

## 新增功能的標準模式

### 新增 Backend API 端點（以新資源 `devices` 為例）

1. 在 `backend/app/models/` 建立 `device.py`（SQLAlchemy 模型）。
2. 在 `backend/app/database/init_db.py` import 新模型以確保建表。
3. 在 `backend/app/api/` 建立 `devices.py`（Pydantic schemas + `APIRouter`）。
4. 在 `backend/app/main.py` 掛載新 router：
   ```python
   app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
   ```

### 新增 Frontend 功能頁面

1. 在 `frontend/src/app/shared/models/` 新增 interface 檔案。
2. 在 `frontend/src/app/shared/services/` 新增 Service（注入 `HttpClient`，URL 從 `environment.apiUrl` 讀取）。
3. 在 `frontend/src/app/pages/` 新增頁面元件目錄。
4. 在 `app.module.ts` 的 `declarations` 陣列新增元件。
5. 在 `app-routing.module.ts` 新增路由。

### 新增 LineBotAI 指令支援

1. 在 `ChatGPTService` 的系統 prompt 新增新 `action` 定義。
2. 在 `LineService._perform_backend_operation()` 新增對應的 `elif action == '...'` 分支。
3. 若需要新的後端呼叫，在 `Home_assistant/` 對應的 service 類別新增方法。

---

## 程式碼品質

- 執行 Python 品質檢查：使用 `.github/skills/code-checklist/SKILL.md` 定義的清單。
- 執行測試覆蓋率：使用 `.github/skills/pytest-coverage/SKILL.md`，目標 100%。
- 提交訊息規範：遵循 `.github/skills/commit-message/SKILL.md`（Conventional Commits）。
- 重構審查：使用 `.github/skills/review-and-refactor/SKILL.md`。
