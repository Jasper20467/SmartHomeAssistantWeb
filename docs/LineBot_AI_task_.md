# LineBot LangGraph Agent 改造任務計畫

## 目標

將現有 `ChatGPTService`（單步 GPT JSON 回應）替換為 **LangGraph ReAct Agent**，
實現多步推理與自主 Tool 呼叫，同時保持後端 API 作為唯一資料層。

---

## 架構說明

```
LINE Webhook
    ↓
LineService（不變）
    ↓
AgentService（新增）
    └── LangGraph ReAct Agent
            ├── Tool: schedule CRUD  →  HomeAssistantClient → Backend API
            └── Tool: consumable CRUD → HomeAssistantClient → Backend API
```

---

## 任務清單

### Phase 1：環境準備

- [x] **P1-1** 在 `LineBotAI/requirements.txt` 新增依賴：
  - `langgraph`
  - `langchain-google-genai`
  - `langchain-core`

- [x] **P1-2** 確認現有 `HomeAssistantClient` 所有方法皆可正常呼叫後端 API（作為 Tool 底層）

---

### Phase 2：建立 Agent Tools

- [x] **P2-1** 新增 `LineBotAI/agent/__init__.py`

- [x] **P2-2** 新增 `LineBotAI/agent/tools.py`，以 `@tool` 裝飾器定義下列 8 個 Tool：

  | Tool 函式名稱 | 包裝的 HomeAssistantClient 方法 |
  |--------------|-------------------------------|
  | `create_schedule` | `ha_client.schedules.create_schedule()` |
  | `get_schedules` | `ha_client.schedules.get_schedules()` |
  | `update_schedule` | `ha_client.schedules.update_schedule()` |
  | `delete_schedule` | `ha_client.schedules.delete_schedule()` |
  | `create_consumable` | `ha_client.consumables.create_consumable()` |
  | `get_consumables` | `ha_client.consumables.get_consumables()` |
  | `update_consumable` | `ha_client.consumables.update_consumable()` |
  | `delete_consumable` | `ha_client.consumables.delete_consumable()` |

  > 每個 Tool 的 docstring 需清楚描述用途與參數，供 LLM 推理使用。

- [x] **P2-3** 新增 `LineBotAI/agent/prompts.py`，定義 Agent 系統 Prompt：
  - 說明助理身份（家用智慧助理）
  - 說明今日日期（Taiwan UTC+8，動態注入）
  - 說明各 Tool 的使用時機

---

### Phase 3：建立 AgentService

- [x] **P3-1** 新增 `LineBotAI/services/agent_service.py`，內容：
  - 從環境變數讀取 `GEMINI_API_KEY` 與 `GEMINI_MODEL`（預設 `gemini-2.0-flash`）
  - 初始化 `ChatGoogleGenerativeAI`（來自 `langchain-google-genai`）
  - 使用 `langgraph.prebuilt.create_react_agent` 建立 Agent
  - 使用 `MemorySaver` 作為 checkpointer（每個 `user_id` 對應獨立 `thread_id`）
  - 提供 `run(user_message: str, user_id: str) -> str` 方法
  - 提供 `clear_history(user_id: str)` 方法

- [x] **P3-2** `AgentService.__init__` 接受 `backend_url` 參數，傳入 `HomeAssistantClient`，再注入各 Tool

---

### Phase 4：整合 LineService

- [x] **P4-1** 修改 `LineBotAI/services/line_service.py`：
  - `__init__` 改為初始化 `AgentService`（而非僅存 `ha_client`）
  - `process_user_message()` 改為呼叫 `agent_service.run(user_message, user_id)`
  - 移除 `_perform_backend_operation()` 與 `_format_backend_response()`（由 Agent 取代）

- [x] **P4-2** 修改 `LineBotAI/app.py`：
  - 移除 `ChatGPTService` 初始化（或保留作備用 fallback）
  - `LineService` 初始化改為傳入 `AgentService`，或在 `LineService` 內部建立

---

### Phase 5：測試與驗證

- [x] **P5-1** 單元測試：`agent/tools.py` 每個 Tool 的正確呼叫路徑（mock `HomeAssistantClient`）

- [x] **P5-2** 整合測試：啟動 debug 容器，透過 `/api/debug/` 端點模擬 LINE 訊息驗證：
  - 單步操作：「幫我建立明天早上 9 點的開會行程」
  - 多步操作：「查看今天的行程，如果沒有就幫我建立一個午餐提醒」
  - 代名詞引用：「把剛才那個行程刪掉」

- [x] **P5-3** 確認對話歷史在多輪對話中正確維持（`user_id` 隔離）

- [x] **P5-4** 更新 `LineBotAI/requirements.txt` 後重建 Docker 映像，確認容器可正常啟動

---

### Phase 6：文件收尾

- [x] **P6-1** 確認 `docs/LineBot_Spec.md` 內容與最終實作一致（目錄結構、API、Tools 清單）

---

### 程式碼審查清理（Post-P6）

- [x] **CL-1** 移除 `LineBotAI/services/api_utils.py`（舊架構產物，已無任何 import）
- [x] **CL-2** 移除 `LineBotAI/Home_assistant/home_assistant_service.py`（標記 deprecated，已無任何 import）
- [x] **CL-3** 移除 `app.py` 中 dead import `from services.chatgpt_service import ChatGPTService`
- [x] **CL-4** 移除 `Home_assistant/__init__.py` 中廢棄別名 `HomeAssistantService = HomeAssistantClient`
- [x] **CL-5** 刪除 `services/chatgpt_service.py`（已完全替換為 LangGraph Agent，不再作為 fallback）
- [x] **CL-6** 刪除 `services/chatgpt_service_backup.py`
- [x] **CL-7** 更新 `verify_tokens.py`：移除 ChatGPT API 測試，改為驗證 `GEMINI_API_KEY` 設定
- [x] **CL-8** 更新 `docker/linebot.Dockerfile`、AWS 部署腳本、`.env`、`README.md`：移除 `CHATGPT_API_KEY`，改為 `GEMINI_API_KEY`

---

## 注意事項

| 項目 | 說明 |
|------|------|
| 資料一致性 | 所有 Tool 必須透過 `HomeAssistantClient` 呼叫 Backend API，禁止直接連 DB |
| 對話持久化 | 初期使用 `MemorySaver`（重啟清除），後續可升級為 `PostgresSaver` |
| 環境變數 | `GEMINI_API_KEY`（必填）與 `GEMINI_MODEL`（選填，預設 `gemini-2.0-flash`）|
