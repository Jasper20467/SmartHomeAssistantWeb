# LineBot 規格文件

## 技術棧

- **框架**: Flask（App Factory 模式）
- **AI 模型**: OpenAI gpt-4.1-nano
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
│   ├── line_service.py     # LINE 訊息收發 + 後端操作協調
│   ├── chatgpt_service.py  # OpenAI API 呼叫 + 對話歷史管理
│   └── api_utils.py        # HomeAssistantClient 封裝
└── Home_assistant/
    ├── client.py           # HomeAssistantClient（整合所有 service）
    ├── base_service.py     # HTTP 請求基底
    ├── schedule_service.py
    ├── consumable_service.py
    └── device_service.py
```

---

## 資料流

```
LINE Webhook → LineService.process_user_message()
    → ChatGPTService.process_message()   # 回傳 action + parameters JSON
    → LineService._perform_backend_operation()
        → HomeAssistantClient → ScheduleService / ConsumableService
            → Backend REST API
    → LineService.reply_to_line()
```

---

## 開發規範

- Flask app 以 `create_app()` 工廠函式建立
- `LineService` 處理 LINE 協定；`ChatGPTService` 處理 AI 邏輯；`HomeAssistantClient` 封裝所有後端呼叫
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
| `CHATGPT_API_KEY` | OpenAI API key | — |
| `BACKEND_API_URL` | 強制指定後端 URL | 無（優先度最高） |
| `DEBUG_MODE` | 除錯模式 | `false` |
| `DEBUG_STAGE` | 除錯階段 | `false` |
| `DOMAIN_NAME` | 生產環境域名 | `smarthome.the-jasperezlife.com` |

---

## ChatGPT 回應格式

GPT 回傳 JSON，包含以下欄位：

```json
{
  "action": "create_schedule",
  "parameters": { ... },
  "reply": "已為您建立排程。"
}
```

**支援的 action 值**：

| action | 說明 |
|--------|------|
| `text_reply` | 純文字回覆 |
| `create_schedule` | 建立排程 |
| `get_schedule` | 查詢排程 |
| `update_schedule` | 更新排程 |
| `delete_schedule` | 刪除排程 |
| `create_consumable` | 建立耗材 |
| `get_consumable` | 查詢耗材 |
| `update_consumable` | 更新耗材 |
| `delete_consumable` | 刪除耗材 |

---

## 對話歷史管理

- 每位 LINE 用戶（`user_id`）維護獨立的 `deque`（最多 5 輪）
- 重啟服務會清除所有歷史（存於記憶體）
- GPT 透過歷史支援代名詞引用（如「它」、「第一個」、「剛才那個」）

### API

```python
# 發送訊息（自動帶入歷史）
chatgpt_service.process_message(user_message, user_id)

# 查看對話歷史
chatgpt_service.get_conversation_history(user_id)

# 清除對話歷史
chatgpt_service.clear_conversation_history(user_id)
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

| 端點 | 說明 |
|------|------|
| `GET /api/debug/config` | 查看當前 URL 配置 |
| `GET /api/debug/backend` | 測試後端 API 連接 |
| `GET /api/health` | 服務健康檢查 |

---

## 新增指令支援流程

1. 在 `ChatGPTService` 系統 prompt 新增新 `action` 定義
2. 在 `LineService._perform_backend_operation()` 新增對應 `elif action == '...'` 分支
3. 若需新的後端呼叫，在 `Home_assistant/` 對應 service 類別新增方法
