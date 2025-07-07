# LINE Bot 代理設定說明

## 概述

本文檔說明如何在 AWS EC2 部署中配置 LINE Bot 的反向代理設定，確保 LINE Bot 能夠正確接收 webhook 事件並提供 API 服務。

## 架構說明

```
Internet → Caddy (Port 80/443) → LINE Bot (Port 5000)
```

## 路由配置

### 1. Caddyfile 設定

```caddy
@linebot {
  path /webhook
  path /linebot/*
  path /api/debug/*
}
reverse_proxy @linebot linebot:5000
```

### 2. 路由說明

| 路由 | 用途 | 代理目標 |
|------|------|----------|
| `/webhook` | LINE Bot webhook 接收端點 | `linebot:5000/webhook` |
| `/linebot/*` | LINE Bot 相關 API | `linebot:5000/linebot/*` |
| `/api/debug/*` | 除錯和測試 API | `linebot:5000/api/debug/*` |

## LINE Bot 設定

### 1. LINE Developers Console 設定

1. 登入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Channel
3. 在 "Messaging API" 設定中：
   - **Webhook URL**: `https://smarthome.the-jasperezlife.com/webhook`
   - **Use webhook**: 啟用
   - **Verify**: 點擊驗證 webhook URL

### 2. 環境變數設定

在 `.env` 檔案中設定：

```env
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
CHATGPT_API_KEY=your_chatgpt_api_key_here
```

## 動態 URL 配置

### 環境變數設定

LINE Bot 支援動態 URL 配置，可根據不同環境自動選擇合適的後端 API URL：

```env
# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
CHATGPT_API_KEY=your_chatgpt_api_key_here

# 後端 API URL 設定（可選）
BACKEND_API_URL=http://backend:8000

# 域名設定（生產環境）
DOMAIN_NAME=smarthome.the-jasperezlife.com

# 除錯模式設定
DEBUG_MODE=false
DEBUG_STAGE=false
```

### URL 選擇邏輯

1. **自定義 URL**: 如果設定了 `BACKEND_API_URL`，直接使用該 URL
2. **除錯模式**: 如果 `DEBUG_MODE=true` 或 `DEBUG_STAGE=true`，使用 `http://backend:8000`
3. **生產模式**: 使用 `https://{DOMAIN_NAME}/api`

### 不同環境的配置

#### 開發環境 (docker-compose.yml)
```yaml
environment:
  - BACKEND_API_URL=http://backend:8000
  - DOMAIN_NAME=localhost
  - DEBUG_MODE=true
  - DEBUG_STAGE=true
```

#### 生產環境 (docker-compose_fromHub.yml)
```yaml
environment:
  - BACKEND_API_URL=http://backend:8000
  - DOMAIN_NAME=smarthome.the-jasperezlife.com
  - DEBUG_MODE=false
  - DEBUG_STAGE=false
```

### 後端 API 整合

LINE Bot 現在可以直接呼叫後端 API 來獲取資料：

- **排程管理**: 獲取用戶的排程資料
- **消耗品管理**: 檢查庫存和消耗品狀態
- **設備控制**: 與智能家居設備互動

### 可用的端點

### 1. 主要端點

- **Webhook**: `https://smarthome.the-jasperezlife.com/webhook`
  - 用於接收 LINE 平台的事件
  - 僅接受 POST 請求

- **健康檢查**: `https://smarthome.the-jasperezlife.com/linebot/health`
  - 檢查 LINE Bot 服務狀態
  - 接受 GET 請求

### 2. 除錯端點

- **除錯測試**: `https://smarthome.the-jasperezlife.com/api/debug/test`
  - 用於測試 LINE Bot 功能
  - 接受 POST 請求

- **後端連接測試**: `https://smarthome.the-jasperezlife.com/api/debug/backend`
  - 測試 LINE Bot 與後端 API 的連接
  - 接受 GET 請求
  - 返回連接狀態和測試結果

- **配置檢查**: `https://smarthome.the-jasperezlife.com/api/debug/config`
  - 檢查當前環境變數配置
  - 接受 GET 請求
  - 返回配置資訊（不包含敏感資料）

## 部署後驗證

### 1. 檢查容器狀態

```bash
docker-compose -f docker-compose_fromHub.yml ps
```

### 2. 檢查 LINE Bot 日誌

```bash
docker-compose -f docker-compose_fromHub.yml logs -f linebot
```

### 3. 檢查 Caddy 日誌

```bash
docker-compose -f docker-compose_fromHub.yml logs -f caddy
```

### 4. 測試後端 API 連接

```bash
# 測試配置
curl https://smarthome.the-jasperezlife.com/api/debug/config

# 測試後端連接
curl https://smarthome.the-jasperezlife.com/api/debug/backend

# 測試 webhook 連接
curl -X POST https://smarthome.the-jasperezlife.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"events": []}'
```

### 5. 測試 ChatGPT 整合

透過 LINE 應用程式發送以下測試訊息：

- `schedule` 或 `排程` - 測試排程功能整合
- `supply` 或 `庫存` - 測試消耗品功能整合
- `hello` - 測試基本 ChatGPT 回應

## 故障排除

### 1. Webhook 驗證失敗

**問題**: LINE Developers Console 中 webhook 驗證失敗

**解決方案**:
1. 確認域名 DNS 設定正確
2. 確認 SSL 憑證已生成
3. 檢查 EC2 安全組設定（開放 80, 443 端口）
4. 檢查 LINE Bot 服務是否正常運行

### 2. 訊息無法接收

**問題**: LINE Bot 無法接收或回覆訊息

**解決方案**:
1. 檢查 LINE_CHANNEL_ACCESS_TOKEN 是否正確
2. 檢查 CHATGPT_API_KEY 是否正確
3. 檢查 backend 服務連接是否正常
4. 查看 LINE Bot 日誌排除錯誤

### 3. SSL 憑證問題

**問題**: HTTPS 連接失敗或憑證錯誤

**解決方案**:
1. 等待 Let's Encrypt 憑證自動生成（可能需要幾分鐘）
2. 檢查 Caddy 日誌確認憑證取得狀態
3. 確認域名指向正確的 EC2 IP

### 4. 後端 API 連接問題

**問題**: LINE Bot 無法連接到後端 API

**解決方案**:
1. 檢查 `BACKEND_API_URL` 環境變數設定
2. 確認後端服務正常運行
3. 使用除錯端點測試連接：`/api/debug/backend`
4. 檢查容器間網路連接：`docker-compose logs backend`

### 5. 環境變數配置問題

**問題**: 動態 URL 配置不正確

**解決方案**:
1. 檢查環境變數設定：`/api/debug/config`
2. 確認 `DOMAIN_NAME` 設定正確
3. 檢查 `DEBUG_MODE` 和 `DEBUG_STAGE` 設定
4. 重新啟動 LINE Bot 服務
4. 重新啟動 LINE Bot 服務

**問題**: HTTPS 連接失敗或憑證錯誤

**解決方案**:
1. 等待 Let's Encrypt 憑證自動生成（可能需要幾分鐘）
2. 檢查 Caddy 日誌確認憑證取得狀態
3. 確認域名指向正確的 EC2 IP

## 安全考量

### 1. 訪問控制

- LINE Bot webhook 端點僅接受來自 LINE 平台的請求
- 除錯端點僅在 DEBUG_MODE=true 時啟用
- 所有外部通信都通過 HTTPS 加密

### 2. 環境變數保護

- 敏感資訊（如 API key）儲存在 `.env` 檔案中
- 不要將 `.env` 檔案提交到版本控制系統

### 3. 網路隔離

- LINE Bot 服務不直接對外開放端口
- 所有外部訪問都通過 Caddy 代理
- 內部服務間通信通過 Docker 網路

## 監控和日誌

### 1. 服務健康監控

```bash
# 檢查所有服務狀態
docker-compose -f docker-compose_fromHub.yml ps

# 檢查特定服務健康狀態
curl https://smarthome.the-jasperezlife.com/linebot/health
```

### 2. 日誌分析

```bash
# 查看 LINE Bot 日誌
docker-compose -f docker-compose_fromHub.yml logs -f linebot

# 查看 Caddy 代理日誌
docker-compose -f docker-compose_fromHub.yml logs -f caddy

# 查看所有服務日誌
docker-compose -f docker-compose_fromHub.yml logs -f
```

## 更新和維護

### 1. 更新 LINE Bot 映像

```bash
# 停止服務
docker-compose -f docker-compose_fromHub.yml down

# 拉取最新映像
docker-compose -f docker-compose_fromHub.yml pull

# 重新啟動服務
docker-compose -f docker-compose_fromHub.yml up -d
```

### 2. 修改 Caddyfile 配置

1. 編輯 `Caddyfile`
2. 重新載入 Caddy 配置：

```bash
docker-compose -f docker-compose_fromHub.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## 相關文檔

- [Docker 時區設定指南](./timezone-setup-guide.md)
- [Docker 推送腳本指南](./docker-push-scripts-guide.md)
- [時區問題故障排除](./docker-timezone-troubleshooting.md)
