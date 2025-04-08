# LineBotAI

LineBotAI 是一個基於 Flask 的應用程式，結合了 LINE Messaging API 與 ChatGPT，提供智能聊天機器人服務。

## 程式架構

`LineBotAI` 模組設計用於整合 LINE Messaging API，提供智慧家庭助理功能。其架構包含以下元件：

1. **Webhook 處理器**：處理來自 LINE 平台的訊息與事件。
2. **訊息處理器**：處理使用者訊息並決定適當的回應。
3. **API 整合**：與外部 API（如智慧家庭設備、天氣服務）介接以獲取或傳送資料。
4. **配置管理**：集中管理 API 金鑰、權杖及其他設定。

## 環境變數

應用程式使用以下環境變數：

- `LINE_CHANNEL_ACCESS_TOKEN`：LINE Messaging API 的存取權杖。
- `CHATGPT_API_KEY`：ChatGPT 的 API 金鑰。
- `BACKEND_API_URL`：後端 API 的 URL（預設值：`http://localhost:8000`）。
- `DEBUG_MODE`：啟用或停用除錯模式（`true` 或 `false`）。
- `DEBUG_STAGE`：啟用或停用除錯階段（`true` 或 `false`）。
- `PORT`：Flask 應用程式的埠號（預設值：`5000`）。

## API 文件

### 1. `/webhook` (POST)
**描述**: 接收來自 LINE 平台的 Webhook 事件，處理訊息並回應。

- **請求格式**:
  ```json
  {
    "events": [
      {
        "replyToken": "string",
        "message": {
          "type": "text",
          "text": "string"
        }
      }
    ]
  }
  ```

- **回應格式**:
  ```json
  {
    "status": "success"
  }
  ```

- **範例**:
  ```bash
  curl -X POST http://localhost:5000/webhook \
    -H "Content-Type: application/json" \
    -d '{
      "events": [
        {
          "replyToken": "12345",
          "message": {
            "type": "text",
            "text": "Hello"
          }
        }
      ]
    }'
  ```

**使用方式**：
- 當使用者透過 LINE 傳送訊息時，LINE Messaging API 會觸發此端點。
- 使用 `replyToken` 回覆訊息給使用者。
- 使用者的訊息內容（`message.text`）會由 ChatGPT 處理，並將回應傳回給使用者。

---

### 2. `/api/health` (GET)
**描述**: 健康檢查端點，用於確認服務是否正常運行。

- **請求格式**: 無需參數。

- **回應格式**:
  ```json
  {
    "status": "ok"
  }
  ```

- **範例**:
  ```bash
  curl http://localhost:5000/api/health
  ```

**使用方式**：
- 使用此端點檢查應用程式是否正常啟動。

---

### 3. `/api/debug/test` (POST)
**描述**: 用於測試與後端或 ChatGPT API 的互動。

- **請求格式**:
  ```json
  {
    "test_mode": "1", // "1" 表示僅測試後端，"2" 表示測試後端與 ChatGPT
    "message": "string", // If test on Backend only, no limit. It only used for ChatGptAPI
    "category": "string", // schedules / consumables
    "operate": "string", // GET/POST/DELETE/PUT
    "content": "{}" // 測試內容，例如查詢的具體問題或指令
  }
  ```

- **回應格式**:
  - 測試模式 1:
    ```json
    {
      "backend": {
        "response": "Backend API response"
      }
    }
    ```
  - 測試模式 2:
    ```json
    {
      "chatgpt": {
        "response": "ChatGPT response"
      },
      "backend": {
        "response": "Backend API response"
      }
    }
    ```

- **範例**:
  ```bash
  curl -X POST http://localhost:5000/api/debug/test \
    -H "Content-Type: application/json" \
    -d '{
      "test_mode": "1",
      "message": "What is the weather today?",
      "category": "consumables",
      "operate": "POST",
      "content": {
        "name": "濾水器濾心便宜貨",
        "category": "空氣清淨機濾網",
        "installation_date": "2025-04-12",
        "lifetime_days": 91,
        "notes": "",
        "id": 99,
        "created_at": "2025-04-08T16:31:34.125246Z",
        "updated_at": "2025-04-08T16:31:34.125246Z",
        "days_remaining": 90
    }
  }'
  ```
```bash
  curl -X POST http://localhost:5000/api/debug/test \
    -H "Content-Type: application/json" \
    -d '{
      "test_mode": "1",
      "message": "What is the weather today?",
      "category": "schedules",
      "operate": "DELETE",
      "content": {"id":3}
  }'
  ```


  - 測試模式 2:
    ```json
    {
      "chatgpt": {
        "response": "ChatGPT response"
      },
      "backend": {
        "response": "Backend API response"
      }
    }
    ```

- **範例**:
  ```bash
  curl -X POST http://localhost:5000/api/debug/test \
    -H "Content-Type: application/json" \
    -d '{
      "test_mode": "2",
      "message": "What is the weather today?"
    }'
  ```

---

## API 測試步驟

為測試與各種 API 的整合，請依以下步驟操作：

1. **LINE Messaging API**：
    - 註冊 LINE 開發者帳號並建立 Messaging API 頻道。
    - 在 LINE 開發者後台設定 Webhook URL 指向您的伺服器。
    - 使用 Postman 或 ngrok 等工具模擬傳入的 Webhook 事件。

2. **智慧家庭設備 API**：
    - 向設備製造商取得 API 文件與憑證。
    - 使用 Postman 測試 API 端點，確保通訊正常。
    - 驗證設備是否正確回應透過 API 發送的指令。

3. **天氣 API**（或其他外部 API）：
    - 向天氣服務提供商註冊並取得 API 金鑰。
    - 使用範例請求測試端點以獲取天氣數據。
    - 確保數據能正確解析並顯示於機器人回應中。

## Debug 階段測試步驟

### 1. 與 backend API 互動

在 Debug 階段測試與 backend API 的互動時，請依以下步驟操作：

1. **確認 backend API 狀態**：
   - 確保 backend API 伺服器已啟動，並可正常接收請求。
   - 使用工具如 Postman 測試 API 端點，確認其回應正確。

2. **模擬請求**：
   - 在 LINE Bot 中觸發與 backend API 互動的功能（例如查詢智慧家庭設備狀態）。
   - 確認 LINE Bot 是否正確發送請求至 backend API。

3. **檢查回應**：
   - 確認 backend API 的回應是否正確傳遞至 LINE Bot。
   - 驗證回應數據是否正確解析並顯示於 LINE Bot 的訊息中。

4. **錯誤處理測試**：
   - 模擬 backend API 回傳錯誤（如 500 錯誤或無效數據）。
   - 確認 LINE Bot 是否能正確處理錯誤並回應使用者。

### 2. 與 backend API 及 ChatGPT API 互動

在 Debug 階段測試與 backend API 和 ChatGPT API 的互動時，請依以下步驟操作：

1. **確認 API 狀態**：
   - 確保 backend API 和 ChatGPT API 均可正常運作。
   - 測試 ChatGPT API 的端點，確認其回應是否符合預期。

2. **模擬複合請求**：
   - 在 LINE Bot 中觸發需要同時與 backend API 和 ChatGPT API 互動的功能（例如智慧助理回答複雜問題）。
   - 確認 LINE Bot 是否正確依序發送請求至 backend API 和 ChatGPT API。

3. **檢查數據流**：
   - 確認 backend API 的回應是否正確傳遞至 ChatGPT API。
   - 驗證 ChatGPT API 的回應是否正確解析並顯示於 LINE Bot 的訊息中。

4. **性能測試**：
   - 測試多次請求的處理速度，確保整體互動流程的性能符合需求。
   - 模擬高負載情境，檢查是否有任何延遲或錯誤。

5. **錯誤處理測試**：
   - 模擬 backend API 或 ChatGPT API 回傳錯誤（如超時或無效數據）。
   - 確認 LINE Bot 是否能正確處理錯誤並回應使用者。

## 配置設定

### 配置項目說明

以下是 `config` 文件中各項設定的詳細說明：

- **`LINE_CHANNEL_SECRET`**：用於驗證來自 LINE 平台請求的密鑰，確保請求的合法性。
- **`LINE_CHANNEL_ACCESS_TOKEN`**：用於透過 LINE Messaging API 發送訊息的存取權杖。
- **`SMART_HOME_API_KEY`**：用於存取智慧家庭設備 API 的密鑰。
- **`WEATHER_API_KEY`**：用於存取天氣服務 API 的密鑰。
- **`WEBHOOK_URL`**：LINE 平台用於傳送 webhook 事件的 URL。

### 配置範例

```json
{
  "LINE_CHANNEL_SECRET": "your-line-channel-secret",
  "LINE_CHANNEL_ACCESS_TOKEN": "your-line-channel-access-token",
  "SMART_HOME_API_KEY": "your-smart-home-api-key",
  "WEATHER_API_KEY": "your-weather-api-key",
  "WEBHOOK_URL": "https://your-webhook-url.com"
}
```

### 配置設定步驟

1. **LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN**：
   - 登入 [LINE Developers Console](https://developers.line.biz/)。
   - 建立 Messaging API 頻道，並取得頻道密鑰與存取權杖。
   - 將這些值填入 `config` 文件中。

2. **SMART_HOME_API_KEY**：
   - 向智慧家庭設備供應商申請 API 密鑰。
   - 確保密鑰具有正確的存取權限。

3. **WEATHER_API_KEY**：
   - 註冊天氣服務提供商（如 OpenWeatherMap）並取得 API 密鑰。
   - 測試 API 是否能正確返回天氣數據。

4. **WEBHOOK_URL**：
   - 確保伺服器的 URL 可公開存取，並設定為 LINE 平台的 webhook URL。
   - 可使用工具如 ngrok 測試本地開發環境。

## 如何運行

1. 複製此專案。
2. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
3. 在 `.env` 文件中設定環境變數。
4. 啟動應用程式：
   ```bash
   python app.py
   ```
5. 在瀏覽器中訪問 `http://localhost:5000`。

## 日誌

日誌預設為 `INFO` 級別。您可以在 `app.py` 文件中修改日誌級別。

## 除錯

- 在 `.env` 文件中啟用 `DEBUG_MODE` 以進入除錯模式。
- 使用 `/api/health` 端點確認應用程式狀態。

## 授權

此專案採用 MIT 授權條款。

## Notes

- Ensure all API keys and tokens are kept secure and not exposed in public repositories.
- Use environment variables or a secure secrets management tool to store sensitive information.
- Regularly test and update the integration with external APIs to handle any changes in their specifications.
