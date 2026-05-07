# Backend 規格文件

## 技術棧

- **框架**: FastAPI + SQLAlchemy (async)
- **語言**: Python 3.10
- **資料驗證**: Pydantic v2
- **資料庫驅動**: asyncpg（PostgreSQL）
- **端口**: 8000（應用）、5678（debugpy）

---

## 目錄結構

```
backend/app/
├── main.py          # FastAPI app 建立、CORS、router 掛載
├── config.py        # 環境設定（os.getenv）
├── api/
│   ├── schedules.py    # Pydantic schemas + APIRouter
│   └── consumables.py  # Pydantic schemas + APIRouter
├── database/
│   ├── database.py     # async engine、session、get_db dependency
│   └── init_db.py      # 建表邏輯（需 import 所有模型）
└── models/
    ├── schedule.py     # SQLAlchemy ORM 模型
    └── consumable.py   # SQLAlchemy ORM 模型
```

---

## 開發規範

- 所有 DB 操作使用 `async/await` + `AsyncSession`
- 依賴注入使用 `Depends(get_db)`
- Pydantic Schema 類別放在對應 router 檔案，命名規則：`Base` / `Create` / `Update` / `Response`
- `Response` 類別設定 `orm_mode = True`（在 `Config` 內）
- 每個資源對應一個 `APIRouter`，在 `main.py` 以 `/api/{resource}` prefix 掛載
- Python 命名：snake_case；資料表名稱複數（`schedules`、`consumables`）
- 所有 `DateTime` 欄位使用 `timezone=True`；時間計算使用台灣時間（UTC+8）
- 環境變數透過 `os.getenv()` 讀取，不寫死敏感資訊

---

## 新增 API 端點標準流程（以 `devices` 為例）

1. 在 `models/` 建立 `device.py`（SQLAlchemy 模型）
2. 在 `database/init_db.py` import 新模型以確保建表
3. 在 `api/` 建立 `devices.py`（Pydantic schemas + `APIRouter`）
4. 在 `main.py` 掛載 router：
   ```python
   app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
   ```

---

## 環境變數

| 變數 | 說明 | 範例 |
|------|------|------|
| `DATABASE_URL` | 資料庫連線字串 | `postgresql+asyncpg://postgres:postgres@db:5432/smarthome` |
| `ENVIRONMENT` | 執行環境 | `development` / `production` |

---

## API 端點

### 基礎端點

| 方法 | URL | 說明 |
|------|-----|------|
| GET | `/` | 歡迎訊息 |
| GET | `/health` | 服務健康檢查 |

**健康檢查回應**：
```json
{ "status": "ok" }
```

---

### Schedules API — `/api/schedules/`

#### GET `/api/schedules/`

獲取所有排程。

**查詢參數**：`skip`（預設 0）、`limit`（預設 100）、`date_filter=YYYY-MM-DD`

**回應範例**：
```json
[
  {
    "id": 1,
    "title": "晨間運動",
    "description": "每日晨間慢跑 30 分鐘",
    "start_time": "2025-07-08T06:00:00Z",
    "end_time": "2025-07-08T06:30:00Z",
    "created_at": "2025-07-07T10:00:00Z",
    "updated_at": "2025-07-07T10:00:00Z"
  }
]
```

#### POST `/api/schedules/`

建立新排程。

**請求體**：
```json
{
  "title": "string（必填）",
  "description": "string（可選）",
  "start_time": "datetime ISO 8601（必填）",
  "end_time": "datetime ISO 8601（可選）"
}
```

**回應**：`201 Created`，回傳完整排程物件。

#### GET `/api/schedules/{id}`

取得單筆排程。`404` 若不存在。

#### PUT `/api/schedules/{id}`

更新排程，所有欄位均可選填。`404` 若不存在。

#### DELETE `/api/schedules/{id}`

刪除排程。**回應**：`204 No Content`。`404` 若不存在。

---

### Consumables API — `/api/consumables/`

#### GET `/api/consumables/`

獲取所有耗材，回應包含計算後的 `days_remaining`。

**查詢參數**：`skip`（預設 0）、`limit`（預設 100）

**回應範例**：
```json
[
  {
    "id": 1,
    "name": "空氣清淨機濾網",
    "category": "家電耗材",
    "installation_date": "2025-06-01",
    "lifetime_days": 90,
    "notes": "HEPA 濾網",
    "created_at": "2025-06-01T08:00:00Z",
    "updated_at": "2025-06-01T08:00:00Z",
    "days_remaining": 54
  }
]
```

#### POST `/api/consumables/`

新增耗材。

**請求體**：
```json
{
  "name": "string（必填）",
  "category": "string（可選）",
  "installation_date": "date（必填）",
  "lifetime_days": "int（必填）",
  "notes": "string（可選）"
}
```

**回應**：`201 Created`。

#### GET `/api/consumables/{id}`

取得單筆耗材。`404` 若不存在。

#### PUT `/api/consumables/{id}`

更新耗材，所有欄位均可選填。`404` 若不存在。

#### DELETE `/api/consumables/{id}`

刪除耗材。**回應**：`204 No Content`。`404` 若不存在。

---

## 自動生成 API 文件

Debug 環境下可直接瀏覽：

- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
