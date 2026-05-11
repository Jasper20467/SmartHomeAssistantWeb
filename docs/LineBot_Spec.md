# LineBot 規格文件

## 技術棧

- **框架**: Flask（App Factory 模式）
- **AI Agent**: LangGraph（ReAct Agent，多步推理 + Tool Use）
- **AI 模型**: Google Gemini（透過 `GEMINI_MODEL` 環境變數設定，預設 `gemini-2.0-flash`）
- **LINE SDK**: line-bot-sdk-python
- **端口**: 5000（應用）、5679（debugpy）

---

## 目錄結構

```
LineBotAI/
├── app.py                  # Flask create_app()，Webhook 入口
├── config/
│   ├── __init__.py
│   └── url_config.py       # get_backend_url()
├── services/
│   ├── line_service.py     # LINE 訊息收發 + Agent 協調
│   └── agent_service.py    # LangGraph ReAct Agent 初始化與執行
├── agent/
│   ├── __init__.py
│   ├── tools.py            # LangGraph Tool 定義（對應 HomeAssistantClient 方法）
│   └── prompts.py          # Agent 系統 Prompt
└── Home_assistant/
    ├── client.py           # HomeAssistantClient（整合所有 service）
    ├── base_service.py     # HTTP 請求基底
    ├── schedule_service.py
    ├── consumable_service.py
    └── device_service.py
```

---

## 資料流

### 舊架構（單步 GPT 呼叫）
```
LINE Webhook → LineService.process_user_message()
    → ChatGPTService.process_message()   # 回傳 action + parameters JSON
    → LineService._perform_backend_operation()
        → HomeAssistantClient → ScheduleService / ConsumableService
            → Backend REST API
    → LineService.reply_to_line()
```

### 新架構（LangGraph ReAct Agent）
```
LINE Webhook → LineService.process_user_message()
    → AgentService.run(user_message, user_id)
        → LangGraph ReAct Agent
            ├── 推理：決定需要哪些 Tool（可多步）
            ├── Tool: create_schedule()    → POST /api/schedules
            ├── Tool: get_schedules()      → GET  /api/schedules
            ├── Tool: update_schedule()    → PUT  /api/schedules/{id}
            ├── Tool: delete_schedule()    → DELETE /api/schedules/{id}
            ├── Tool: create_consumable()  → POST /api/consumables
            ├── Tool: get_consumables()    → GET  /api/consumables
            ├── Tool: update_consumable()  → PUT  /api/consumables/{id}
            └── Tool: delete_consumable()  → DELETE /api/consumables/{id}
        → 彙整結果，生成最終回覆文字
    → LineService.reply_to_line()
```

> **設計原則**：LangGraph Agent 負責多步推理與 Tool 選擇；Backend REST API 仍為唯一資料層，所有 Tool 透過 `HomeAssistantClient` 呼叫後端，不直接存取資料庫。

---

## 開發規範

- Flask app 以 `create_app()` 工廠函式建立
- `LineService` 處理 LINE 協定；`AgentService` 執行 LangGraph Agent；`HomeAssistantClient` 封裝所有後端呼叫
- Agent Tools 定義在 `agent/tools.py`，每個 Tool 包裝 `HomeAssistantClient` 對應方法
- Agent 系統 Prompt 集中管理於 `agent/prompts.py`
- 對話歷史（`user_id` 隔離）由 LangGraph `MemorySaver` 或外部 checkpointer 管理
- Backend URL 一律透過 `config/url_config.py` 的 `get_backend_url()` 取得

---

## 動態 URL 配置

`get_backend_url()` 優先順序：

```python
def get_backend_url():
    # 1. 優先使用自定義 URL
    custom_url = os.getenv('BACKEND_API_URL')
    if custom_url and custom_url.strip():
        return custom_url

    # 2. 除錯模式使用容器間通信
    if os.getenv('DEBUG_MODE', 'false').lower() == 'true' or \
       os.getenv('DEBUG_STAGE', 'false').lower() == 'true':
        return 'http://backend:8000'

    # 3. 生產模式使用域名 URL
    domain = os.getenv('DOMAIN_NAME', 'smarthome.the-jasperezlife.com')
    return f'https://{domain}/api'
```

---

## 環境變數

| 變數 | 用途 | 預設值 |
|------|------|--------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE channel token | — |
| `GEMINI_API_KEY` | Google Gemini API 金鑰 | — |
| `GEMINI_MODEL` | Gemini 模型名稱 | `gemini-2.0-flash` |
| `BACKEND_API_URL` | 強制指定後端 URL | 無（優先度最高） |
| `DEBUG_MODE` | 除錯模式 | `false` |
| `DEBUG_STAGE` | 除錯階段 | `false` |
| `DOMAIN_NAME` | 生產環境域名 | `smarthome.the-jasperezlife.com` |

---

## LangGraph Agent Tools

Agent 不再回傳固定格式 JSON，而是自主決定呼叫哪些 Tool、以何種順序執行，最後彙整結果生成自然語言回覆。

**已定義 Tools**（位於 `agent/tools.py`）：

| Tool 名稱 | 說明 | 對應 Backend API |
|-----------|------|------------------|
| `create_schedule` | 建立排程 | `POST /api/schedules` |
| `get_schedules` | 查詢排程（可傳 `date` 篩選）| `GET /api/schedules` |
| `update_schedule` | 更新排程（需傳 `id`）| `PUT /api/schedules/{id}` |
| `delete_schedule` | 刪除排程（需傳 `id`）| `DELETE /api/schedules/{id}` |
| `create_consumable` | 建立耗材 | `POST /api/consumables` |
| `get_consumables` | 查詢耗材 | `GET /api/consumables` |
| `update_consumable` | 更新耗材（需傳 `id`）| `PUT /api/consumables/{id}` |
| `delete_consumable` | 刪除耗材（需傳 `id`）| `DELETE /api/consumables/{id}` |

> Agent 可在單次對話中連續呼叫多個 Tool，例如「先查詢有無衝突，再決定是否建立排程」。

---

## 對話歷史管理

- 每位 LINE 用戶（`user_id`）使用獨立的 LangGraph `thread_id`
- 歷史由 LangGraph checkpointer 管理，支援代名詞引用（如「它」、「第一個」、「剛才那個」）
- 預設使用 `MemorySaver`（記憶體，重啟後清除）；未來可替換為 `PostgresSaver` 持久化

### API

```python
# 執行 Agent（自動帶入該用戶歷史）
agent_service.run(user_message, user_id)

# 清除特定用戶歷史
agent_service.clear_history(user_id)
```

---

## LINE Webhook 設定

LINE Developers Console 設定：

- **Webhook URL**: `https://{DOMAIN_NAME}/webhook`
- **Use webhook**: 啟用

### Caddy 反向代理路由

```caddy
@linebot {
  path /webhook
  path /linebot/*
  path /api/debug/*
}
reverse_proxy @linebot linebot:5000
```

---

## 除錯端點

| 端點 | 說明 | 限制 |
|------|------|------|
| `GET /api/health` | 服務健康檢查 | — |
| `GET /linebot/health` | LineBot 詳細健康檢查（含 backend_url、debug 狀態）| — |
| `POST /api/debug/chat` | 模擬 LINE 用戶訊息，直接呼叫 Agent 並回傳文字回覆 | `DEBUG_STAGE=true` |

### `/api/debug/chat` 請求格式

```json
// Request
{
  "user_message": "幫我查看今天的行程",
  "user_id": "test_user_001"   // 選填，預設 "debug_user"
}

// Response
{
  "reply": "今天目前沒有排程。",
  "user_id": "test_user_001"
}
```

---

## 新增指令支援流程

1. 在 `Home_assistant/` 對應 service 類別新增方法（例如 `schedule_service.py`）
2. 在 `agent/tools.py` 新增對應的 `@tool` 裝飾器函式，包裝上一步的方法
3. 將新 Tool 加入 `AgentService` 的 tools 清單
4. 視需要在 `agent/prompts.py` 更新系統 Prompt，說明新功能的使用時機
