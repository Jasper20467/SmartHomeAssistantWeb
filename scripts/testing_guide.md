# 整合測試腳本使用指南

## 概述

整合了所有測試腳本為兩個主要的測試套件：
- `test_debug_environment.py` - Debug 環境測試
- `test_production_environment.py` - Production 環境測試

## 使用方法

### 快速狀態檢查

```bash
# 檢查測試環境狀態
python scripts/test_summary.py
```

### Debug 環境測試

```bash
# 確保 Docker 容器正在運行
cd SmartHomeAssistantWeb
docker-compose up -d

# 執行 Debug 環境測試
python scripts/test_debug_environment.py
```

**測試內容：**
- ✅ 容器狀態檢查
- ✅ 基礎服務檢查 (frontend, backend, linebot)
- ✅ API 端點測試
- ✅ CRUD 操作測試 (schedules, consumables)
- ✅ LineBot 配置測試
- ✅ 服務整合測試

### Production 環境測試

```bash
# 測試預設 Production 環境
python scripts/test_production_environment.py

# 測試自訂域名
python scripts/test_production_environment.py --domain https://your-domain.com
```

**測試內容：**
- ✅ 基礎服務檢查
- ✅ API 端點測試
- ✅ LineBot 服務測試
- ✅ 配置驗證 (HTTPS, 安全頭)
- ✅ 性能測試
- ✅ 安全性檢查
- ✅ 服務可用性測試

## 輸出範例

### Debug 環境測試輸出
```
🏠 Smart Home Assistant Debug Environment Test Suite
============================================================
🕐 開始時間: 2025-07-07 18:15:30
🎯 目標環境: Debug (localhost)

📋 容器狀態檢查...
----------------------------------------
   運行中的服務: frontend, backend, linebot, postgres
   ✅ 所有必要服務都在運行
✅ 容器狀態檢查 - 通過

📋 基礎服務檢查...
----------------------------------------
   ✅ 前端: HTTP 200
   ✅ Backend Health: HTTP 200
   ✅ LineBot Health: HTTP 200
✅ 基礎服務檢查 - 通過
```

### Production 環境測試輸出
```
🏭 Smart Home Assistant Production Environment Test Suite
============================================================
🕐 開始時間: 2025-07-07 18:20:45
🎯 目標環境: Production (https://smarthome.the-jasperezlife.com)

📋 基礎服務檢查...
----------------------------------------
   ✅ 前端服務: HTTP 200
      ⏱️  響應時間: 0.85s (良好)
   ✅ Backend Health: HTTP 200
      ⏱️  響應時間: 0.45s (良好)
   ✅ LineBot Health: HTTP 200
      ⏱️  響應時間: 0.32s (良好)
✅ 基礎服務檢查 - 通過
```

## 依賴套件

確保安裝了必要的 Python 套件：
```bash
pip install requests
```

## 故障排除

### Debug 環境常見問題
- **容器未運行**: 執行 `docker-compose up -d`
- **端口衝突**: 檢查 `localhost:80` 是否被其他服務占用
- **API 連接失敗**: 確認 backend 容器正常啟動

### Production 環境常見問題
- **DNS 解析失敗**: 檢查域名配置
- **SSL 證書問題**: 確認 HTTPS 證書有效
- **502 錯誤**: Backend 服務可能未正常運行

## 維護

- 定期執行測試以確保系統健康
- 在部署後執行 Production 測試
- 開發過程中執行 Debug 測試
- 根據需要調整測試參數和閾值
