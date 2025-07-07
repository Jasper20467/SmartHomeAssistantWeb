# LINE Bot 動態 URL 配置更新說明

## 概述

本次更新為 LINE Bot 添加了動態 URL 配置功能，使其能夠根據不同的環境（開發/除錯/生產）自動選擇正確的後端 API URL，並整合 Smart Home Assistant 的後端服務。

## 主要更新

### 1. 動態 URL 配置邏輯

LINE Bot 現在支援以下 URL 選擇策略：

```python
def get_backend_url():
    # 1. 優先使用自定義 URL
    custom_url = os.getenv('BACKEND_API_URL')
    if custom_url and custom_url.strip():
        return custom_url
    
    # 2. 除錯模式使用容器間通信
    debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    debug_stage = os.getenv('DEBUG_STAGE', 'false').lower() == 'true'
    
    if debug_mode or debug_stage:
        return 'http://backend:8000'
    
    # 3. 生產模式使用域名 URL
    domain = os.getenv('DOMAIN_NAME', 'smarthome.the-jasperezlife.com')
    return f'https://{domain}/api'
```

### 2. 環境變數配置

新增支援的環境變數：

| 變數名稱 | 用途 | 預設值 |
|----------|------|---------|
| `BACKEND_API_URL` | 自定義後端 API URL | 無 |
| `DOMAIN_NAME` | 生產環境域名 | `smarthome.the-jasperezlife.com` |
| `DEBUG_MODE` | 除錯模式開關 | `false` |
| `DEBUG_STAGE` | 除錯階段開關 | `false` |

### 3. 後端 API 整合

LINE Bot 現在可以直接調用 Smart Home Assistant 的後端 API：

- **排程管理**: 與行程表單系統整合
- **消耗品管理**: 與庫存管理系統整合
- **設備控制**: 與智能家居設備整合

### 4. 新增除錯端點

增加了以下除錯端點：

- `/api/debug/backend` - 測試後端 API 連接
- `/api/debug/config` - 檢查當前配置
- `/api/debug/test` - 原有的除錯測試功能

### 5. ChatGPT 服務增強

更新了 ChatGPT 服務：

- 支援後端 API 整合
- 根據用戶訊息內容智能獲取相關資料
- 使用更新的 GPT-3.5-turbo 模型

## 配置檔案更新

### 1. docker-compose.yml (開發環境)

```yaml
environment:
  - BACKEND_API_URL=http://backend:8000
  - DOMAIN_NAME=localhost
  - DEBUG_MODE=true
  - DEBUG_STAGE=true
```

### 2. docker-compose_fromHub.yml (生產環境)

```yaml
environment:
  - BACKEND_API_URL=http://backend:8000
  - DOMAIN_NAME=smarthome.the-jasperezlife.com
  - DEBUG_MODE=false
  - DEBUG_STAGE=false
```

### 3. Caddyfile

更新了路由優先順序，確保 LINE Bot 的除錯端點正確代理：

```caddy
@linebot {
  path /webhook
  path /linebot/*
  path /api/debug/*
}
reverse_proxy @linebot linebot:5000

@api {
  path /api/*
}
reverse_proxy @api backend:8000
```

## 測試驗證

### 1. 配置測試

執行測試腳本驗證配置邏輯：

```bash
python scripts/test_linebot_config.py
```

### 2. 部署後測試

部署後可使用以下端點測試：

```bash
# 檢查配置
curl https://smarthome.the-jasperezlife.com/api/debug/config

# 測試後端連接
curl https://smarthome.the-jasperezlife.com/api/debug/backend

# 測試 webhook
curl -X POST https://smarthome.the-jasperezlife.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"events": []}'
```

## 部署指南

### 1. 重新建置映像

使用更新的推送腳本：

```bash
# 快速推送
.\scripts\quick_push.ps1

# 完整推送
.\scripts\push_docker_images.ps1
```

### 2. 更新部署

```bash
# 停止現有服務
docker-compose -f docker-compose_fromHub.yml down

# 拉取最新映像
docker-compose -f docker-compose_fromHub.yml pull

# 重新啟動服務
docker-compose -f docker-compose_fromHub.yml up -d
```

### 3. 驗證部署

```bash
# 檢查服務狀態
docker-compose -f docker-compose_fromHub.yml ps

# 檢查日誌
docker-compose -f docker-compose_fromHub.yml logs -f linebot
```

## 相容性說明

- ✅ 向後相容：原有的 `BACKEND_API_URL` 環境變數仍然有效
- ✅ 預設行為：未設定環境變數時使用合理預設值
- ✅ 除錯友好：提供多個除錯端點方便故障排除

## 注意事項

1. **環境變數優先順序**：`BACKEND_API_URL` > 除錯模式 > 生產模式
2. **域名設定**：確保生產環境的 `DOMAIN_NAME` 指向正確的域名
3. **SSL 憑證**：生產環境自動使用 HTTPS，確保 Let's Encrypt 憑證正常
4. **容器間通信**：除錯模式使用容器名稱 `backend:8000`

## 後續計畫

1. 增加更多後端 API 整合功能
2. 實現 LINE Bot 的智能回應模式
3. 添加使用者偏好設定
4. 實現排程提醒功能

---

**文檔版本**: 1.0  
**更新日期**: 2025-07-07  
**相關文檔**: [LINE Bot 代理設定說明](./linebot-proxy-setup.md)
