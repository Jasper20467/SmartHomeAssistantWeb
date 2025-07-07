# Smart Home Assistant Backend API 文檔

## 概述

Smart Home Assistant Backend API 提供智慧家庭管理功能，包括排程管理和消耗品追蹤。API 使用 FastAPI 框架建構，支援異步操作和自動 API 文檔生成。

## 環境配置

### Debug 環境
- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api`
- **完整 URL**: `http://localhost:8000/api`

### Production 環境
- **內部訪問**: `http://backend:8000` （僅供 Docker 服務間通訊）
- **外部訪問**: 透過前端代理或 LineBot 服務
- **注意**: Production 環境下 Backend API 不對外直接暴露

## 基礎端點

### 1. 根端點

**URL**: `/`
**方法**: `GET`
**描述**: API 歡迎訊息

#### 請求範例
```bash
# Debug
curl http://localhost:8000/

# Production (內部)
curl http://backend:8000/
```

#### 回應範例
```json
{
  "message": "Welcome to Smart Home Assistant API"
}
```

### 2. 健康檢查

**URL**: `/health`
**方法**: `GET`
**描述**: 檢查 API 服務狀態

#### 請求範例
```bash
# Debug
curl http://localhost:8000/health

# Production (內部)
curl http://backend:8000/health
```

#### 回應範例
```json
{
  "status": "ok"
}
```

## Schedules API

排程管理 API，用於創建、讀取、更新和刪除排程項目。

### 1. 獲取所有排程

**URL**: `/api/schedules/`
**方法**: `GET`
**描述**: 獲取所有排程，支援分頁

#### 查詢參數
- `skip` (int, 可選): 跳過的項目數，預設 0
- `limit` (int, 可選): 返回的最大項目數，預設 100

#### 請求範例
```bash
# Debug - 獲取所有排程
curl http://localhost:8000/api/schedules/

# Debug - 分頁查詢
curl "http://localhost:8000/api/schedules/?skip=0&limit=10"

# Production (內部)
curl http://backend:8000/api/schedules/
```

#### 回應範例
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
  },
  {
    "id": 2,
    "title": "工作會議",
    "description": "每週項目進度討論",
    "start_time": "2025-07-08T14:00:00Z",
    "end_time": "2025-07-08T15:00:00Z",
    "created_at": "2025-07-07T11:00:00Z",
    "updated_at": "2025-07-07T11:00:00Z"
  }
]
```

### 2. 創建新排程

**URL**: `/api/schedules/`
**方法**: `POST`
**描述**: 創建一個新的排程項目

#### 請求體
```json
{
  "title": "string (必填)",
  "description": "string (可選)",
  "start_time": "datetime (必填, ISO 8601 格式)",
  "end_time": "datetime (可選, ISO 8601 格式)"
}
```

#### 請求範例
```bash
# Debug
curl -X POST http://localhost:8000/api/schedules/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "晚餐約會",
    "description": "與朋友在餐廳聚餐",
    "start_time": "2025-07-08T19:00:00Z",
    "end_time": "2025-07-08T21:00:00Z"
  }'

# Production (內部)
curl -X POST http://backend:8000/api/schedules/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "晚餐約會",
    "description": "與朋友在餐廳聚餐",
    "start_time": "2025-07-08T19:00:00Z",
    "end_time": "2025-07-08T21:00:00Z"
  }'
```

#### 回應範例
**狀態碼**: `201 Created`
```json
{
  "id": 3,
  "title": "晚餐約會",
  "description": "與朋友在餐廳聚餐",
  "start_time": "2025-07-08T19:00:00Z",
  "end_time": "2025-07-08T21:00:00Z",
  "created_at": "2025-07-07T12:30:00Z",
  "updated_at": "2025-07-07T12:30:00Z"
}
```

### 3. 獲取特定排程

**URL**: `/api/schedules/{schedule_id}`
**方法**: `GET`
**描述**: 根據 ID 獲取特定排程

#### 路徑參數
- `schedule_id` (int): 排程 ID

#### 請求範例
```bash
# Debug
curl http://localhost:8000/api/schedules/1

# Production (內部)
curl http://backend:8000/api/schedules/1
```

#### 回應範例
```json
{
  "id": 1,
  "title": "晨間運動",
  "description": "每日晨間慢跑 30 分鐘",
  "start_time": "2025-07-08T06:00:00Z",
  "end_time": "2025-07-08T06:30:00Z",
  "created_at": "2025-07-07T10:00:00Z",
  "updated_at": "2025-07-07T10:00:00Z"
}
```

#### 錯誤回應
**狀態碼**: `404 Not Found`
```json
{
  "detail": "Schedule not found"
}
```

### 4. 更新排程

**URL**: `/api/schedules/{schedule_id}`
**方法**: `PUT`
**描述**: 更新現有排程

#### 路徑參數
- `schedule_id` (int): 排程 ID

#### 請求體
```json
{
  "title": "string (可選)",
  "description": "string (可選)",
  "start_time": "datetime (可選)",
  "end_time": "datetime (可選)"
}
```

#### 請求範例
```bash
# Debug
curl -X PUT http://localhost:8000/api/schedules/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "晨間運動 - 更新",
    "description": "每日晨間慢跑 45 分鐘",
    "start_time": "2025-07-08T06:00:00Z",
    "end_time": "2025-07-08T06:45:00Z"
  }'

# Production (內部)
curl -X PUT http://backend:8000/api/schedules/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "晨間運動 - 更新",
    "description": "每日晨間慢跑 45 分鐘"
  }'
```

#### 回應範例
```json
{
  "id": 1,
  "title": "晨間運動 - 更新",
  "description": "每日晨間慢跑 45 分鐘",
  "start_time": "2025-07-08T06:00:00Z",
  "end_time": "2025-07-08T06:45:00Z",
  "created_at": "2025-07-07T10:00:00Z",
  "updated_at": "2025-07-07T13:00:00Z"
}
```

### 5. 刪除排程

**URL**: `/api/schedules/{schedule_id}`
**方法**: `DELETE`
**描述**: 刪除指定的排程

#### 路徑參數
- `schedule_id` (int): 排程 ID

#### 請求範例
```bash
# Debug
curl -X DELETE http://localhost:8000/api/schedules/1

# Production (內部)
curl -X DELETE http://backend:8000/api/schedules/1
```

#### 回應範例
**狀態碼**: `204 No Content`
（無回應內容）

#### 錯誤回應
**狀態碼**: `404 Not Found`
```json
{
  "detail": "Schedule not found"
}
```

## Consumables API

消耗品管理 API，用於追蹤家庭消耗品的安裝日期、使用期限和剩餘天數。

### 1. 獲取所有消耗品

**URL**: `/api/consumables/`
**方法**: `GET`
**描述**: 獲取所有消耗品，包含剩餘天數計算

#### 查詢參數
- `skip` (int, 可選): 跳過的項目數，預設 0
- `limit` (int, 可選): 返回的最大項目數，預設 100

#### 請求範例
```bash
# Debug
curl http://localhost:8000/api/consumables/

# Debug - 分頁查詢
curl "http://localhost:8000/api/consumables/?skip=0&limit=5"

# Production (內部)
curl http://backend:8000/api/consumables/
```

#### 回應範例
```json
[
  {
    "id": 1,
    "name": "空氣清淨機濾網",
    "category": "家電耗材",
    "installation_date": "2025-06-01",
    "lifetime_days": 90,
    "notes": "HEPA 濾網，需定期更換",
    "created_at": "2025-06-01T08:00:00Z",
    "updated_at": "2025-06-01T08:00:00Z",
    "days_remaining": 54
  },
  {
    "id": 2,
    "name": "濾水器濾心",
    "category": "廚房用品",
    "installation_date": "2025-05-15",
    "lifetime_days": 180,
    "notes": "RO 逆滲透濾心",
    "created_at": "2025-05-15T10:00:00Z",
    "updated_at": "2025-05-15T10:00:00Z",
    "days_remaining": 127
  }
]
```

### 2. 創建新消耗品

**URL**: `/api/consumables/`
**方法**: `POST`
**描述**: 添加新的消耗品項目

#### 請求體
```json
{
  "name": "string (必填)",
  "category": "string (必填)",
  "installation_date": "date (必填, YYYY-MM-DD 格式)",
  "lifetime_days": "integer (必填)",
  "notes": "string (可選)"
}
```

#### 請求範例
```bash
# Debug
curl -X POST http://localhost:8000/api/consumables/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "洗衣機清潔劑",
    "category": "清潔用品",
    "installation_date": "2025-07-07",
    "lifetime_days": 30,
    "notes": "每月使用一次"
  }'

# Production (內部)
curl -X POST http://backend:8000/api/consumables/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "冷氣濾網",
    "category": "家電耗材",
    "installation_date": "2025-07-07",
    "lifetime_days": 60,
    "notes": "客廳冷氣機濾網"
  }'
```

#### 回應範例
**狀態碼**: `201 Created`
```json
{
  "id": 3,
  "name": "洗衣機清潔劑",
  "category": "清潔用品",
  "installation_date": "2025-07-07",
  "lifetime_days": 30,
  "notes": "每月使用一次",
  "created_at": "2025-07-07T14:00:00Z",
  "updated_at": "2025-07-07T14:00:00Z",
  "days_remaining": 30
}
```

### 3. 獲取特定消耗品

**URL**: `/api/consumables/{consumable_id}`
**方法**: `GET`
**描述**: 根據 ID 獲取特定消耗品

#### 路徑參數
- `consumable_id` (int): 消耗品 ID

#### 請求範例
```bash
# Debug
curl http://localhost:8000/api/consumables/1

# Production (內部)
curl http://backend:8000/api/consumables/1
```

#### 回應範例
```json
{
  "id": 1,
  "name": "空氣清淨機濾網",
  "category": "家電耗材",
  "installation_date": "2025-06-01",
  "lifetime_days": 90,
  "notes": "HEPA 濾網，需定期更換",
  "created_at": "2025-06-01T08:00:00Z",
  "updated_at": "2025-06-01T08:00:00Z",
  "days_remaining": 54
}
```

#### 錯誤回應
**狀態碼**: `404 Not Found`
```json
{
  "detail": "Consumable not found"
}
```

### 4. 更新消耗品

**URL**: `/api/consumables/{consumable_id}`
**方法**: `PUT`
**描述**: 更新現有消耗品資訊

#### 路徑參數
- `consumable_id` (int): 消耗品 ID

#### 請求體
```json
{
  "name": "string (可選)",
  "category": "string (可選)",
  "installation_date": "date (可選)",
  "lifetime_days": "integer (可選)",
  "notes": "string (可選)"
}
```

#### 請求範例
```bash
# Debug
curl -X PUT http://localhost:8000/api/consumables/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "空氣清淨機濾網 - 高效型",
    "notes": "HEPA 濾網，高效除PM2.5",
    "lifetime_days": 120
  }'

# Production (內部)
curl -X PUT http://backend:8000/api/consumables/1 \
  -H "Content-Type: application/json" \
  -d '{
    "installation_date": "2025-07-01",
    "notes": "已更換新濾網"
  }'
```

#### 回應範例
```json
{
  "id": 1,
  "name": "空氣清淨機濾網 - 高效型",
  "category": "家電耗材",
  "installation_date": "2025-06-01",
  "lifetime_days": 120,
  "notes": "HEPA 濾網，高效除PM2.5",
  "created_at": "2025-06-01T08:00:00Z",
  "updated_at": "2025-07-07T15:00:00Z",
  "days_remaining": 84
}
```

### 5. 刪除消耗品

**URL**: `/api/consumables/{consumable_id}`
**方法**: `DELETE`
**描述**: 刪除指定的消耗品

#### 路徑參數
- `consumable_id` (int): 消耗品 ID

#### 請求範例
```bash
# Debug
curl -X DELETE http://localhost:8000/api/consumables/1

# Production (內部)
curl -X DELETE http://backend:8000/api/consumables/1
```

#### 回應範例
**狀態碼**: `204 No Content`
（無回應內容）

#### 錯誤回應
**狀態碼**: `404 Not Found`
```json
{
  "detail": "Consumable not found"
}
```

## 錯誤處理

### 常見錯誤狀態碼

- **400 Bad Request**: 請求格式錯誤或缺少必填欄位
- **404 Not Found**: 找不到指定的資源
- **422 Unprocessable Entity**: 資料驗證失敗
- **500 Internal Server Error**: 伺服器內部錯誤

### 錯誤回應格式

```json
{
  "detail": "錯誤描述訊息"
}
```

或包含更詳細的驗證錯誤：

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 資料模型

### Schedule 模型
```json
{
  "id": "integer (自動生成)",
  "title": "string (必填)",
  "description": "string (可選)",
  "start_time": "datetime (必填, ISO 8601 格式)",
  "end_time": "datetime (可選, ISO 8601 格式)",
  "created_at": "datetime (自動生成)",
  "updated_at": "datetime (自動更新)"
}
```

### Consumable 模型
```json
{
  "id": "integer (自動生成)",
  "name": "string (必填)",
  "category": "string (必填)",
  "installation_date": "date (必填, YYYY-MM-DD 格式)",
  "lifetime_days": "integer (必填)",
  "notes": "string (可選)",
  "created_at": "datetime (自動生成)",
  "updated_at": "datetime (自動更新)",
  "days_remaining": "integer (計算得出)"
}
```

## 使用範例

### Python 範例
```python
import requests

# Debug 環境
base_url = "http://localhost:8000/api"

# 獲取所有排程
response = requests.get(f"{base_url}/schedules/")
schedules = response.json()

# 創建新排程
new_schedule = {
    "title": "會議",
    "start_time": "2025-07-08T10:00:00Z"
}
response = requests.post(f"{base_url}/schedules/", json=new_schedule)
created_schedule = response.json()

# 獲取消耗品並檢查到期項目
response = requests.get(f"{base_url}/consumables/")
consumables = response.json()
expiring_soon = [c for c in consumables if c["days_remaining"] <= 7]
```

### JavaScript 範例
```javascript
// Debug 環境
const baseURL = 'http://localhost:8000/api';

// 獲取所有消耗品
async function getConsumables() {
  const response = await fetch(`${baseURL}/consumables/`);
  const consumables = await response.json();
  return consumables;
}

// 創建新消耗品
async function createConsumable(data) {
  const response = await fetch(`${baseURL}/consumables/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  return await response.json();
}
```

## 注意事項

1. **時區處理**: 所有 datetime 欄位使用 UTC 時間，建議在前端進行時區轉換
2. **分頁**: 大型資料集建議使用 `skip` 和 `limit` 參數進行分頁查詢
3. **剩餘天數**: Consumables API 會自動計算並返回剩餘天數
4. **Production 安全**: Production 環境下 Backend API 僅供內部服務使用，不直接對外暴露
5. **資料驗證**: 所有請求都會進行資料格式驗證，請確保提供正確的資料類型

## 自動化 API 文檔

在 Debug 環境中，FastAPI 提供自動生成的互動式 API 文檔：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

這些文檔提供完整的 API 規格說明和測試介面。
