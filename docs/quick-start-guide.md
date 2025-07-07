# Smart Home Assistant 操作指南

## 快速開始

### Debug Mode (本地開發)

1. **啟動服務**
   ```bash
   docker-compose up -d
   ```

2. **檢查服務狀態**
   ```bash
   docker ps
   ```

3. **運行整合測試**
   ```bash
   python scripts/test_integration.py --mode debug
   ```

4. **存取服務**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000
   - LineBot: http://localhost:5000
   - Database: localhost:5432

### Production Mode (生產環境)

1. **部署到生產環境**
   ```bash
   cd scripts/DeployOn_AWS_Ec2
   docker-compose -f docker-compose_fromHub.yml up -d
   ```

2. **測試生產配置**
   ```bash
   python ../test_integration.py --mode production
   ```

## 常用命令

### 服務管理
```bash
# 啟動所有服務
docker-compose up -d

# 重啟特定服務
docker-compose restart backend

# 查看服務日誌
docker logs smarthomeassistantweb-backend-1

# 停止所有服務
docker-compose down
```

### 測試命令
```bash
# 運行完整整合測試
python scripts/test_integration.py --mode debug

# 運行 LineBot 配置測試
python scripts/test_linebot_config.py

# 運行配置驗證
python scripts/test_production_config.py

# 一鍵測試 (Windows)
scripts/test_debug_mode.ps1

# 一鍵測試 (Linux/Mac)
scripts/test_debug_mode.sh
```

### 開發工作流

1. **修改代碼後重建服務**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

2. **僅重建特定服務**
   ```bash
   docker-compose up -d --build backend
   ```

3. **查看實時日誌**
   ```bash
   docker-compose logs -f backend
   ```

## 故障排除

### 常見問題

1. **Backend 無法連接資料庫**
   - 檢查 DATABASE_URL 是否使用 `postgresql+asyncpg://`
   - 確認 PostgreSQL 服務是否正常運行

2. **Frontend 無法存取 Backend API**
   - 確認所有服務都在 `app-network` 中
   - 檢查 Nginx 配置是否正確代理到 `backend:8000`

3. **LineBot 無法連接 Backend**
   - 檢查 BACKEND_API_URL 環境變數
   - 確認 DEBUG_MODE 和 DOMAIN_NAME 設定正確

### 診斷步驟

1. **檢查服務狀態**
   ```bash
   docker ps
   docker-compose ps
   ```

2. **查看服務日誌**
   ```bash
   docker logs smarthomeassistantweb-backend-1
   docker logs smarthomeassistantweb-frontend-1
   docker logs smarthomeassistantweb-linebot-1
   ```

3. **測試網路連接**
   ```bash
   # 進入容器測試網路
   docker exec -it smarthomeassistantweb-frontend-1 ping backend
   ```

4. **運行自動化測試**
   ```bash
   python scripts/test_integration.py --mode debug
   ```

## 環境變數配置

### Debug Mode
```env
# Backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/smarthome
ENVIRONMENT=development

# LineBot
BACKEND_API_URL=http://backend:8000
DOMAIN_NAME=localhost
DEBUG_MODE=true
DEBUG_STAGE=true
```

### Production Mode
```env
# Backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/smarthome
ENVIRONMENT=production

# LineBot
BACKEND_API_URL=http://backend:8000
DOMAIN_NAME=smarthome.the-jasperezlife.com
DEBUG_MODE=false
DEBUG_STAGE=false
```

## 監控和日誌

### 服務健康檢查
- Backend: http://localhost:8000/health
- LineBot: http://localhost:5000/linebot/health
- Frontend: http://localhost:80

### 日誌位置
- Backend: `docker logs smarthomeassistantweb-backend-1`
- LineBot: `docker logs smarthomeassistantweb-linebot-1`
- Frontend: `docker logs smarthomeassistantweb-frontend-1`
- Database: `docker logs smarthomeassistantweb-db-1`

## 最佳實踐

1. **定期運行測試**
   ```bash
   # 每次修改後運行
   python scripts/test_integration.py --mode debug
   ```

2. **保持環境變數同步**
   - 確保 debug 和 production 環境變數正確設定
   - 使用 `.env` 文件管理敏感資訊

3. **定期更新依賴**
   ```bash
   # 更新 Docker 映像
   docker-compose pull
   docker-compose up -d
   ```

4. **備份資料庫**
   ```bash
   # 匯出資料庫
   docker exec smarthomeassistantweb-db-1 pg_dump -U postgres smarthome > backup.sql
   ```

## 聯絡資訊

如有問題，請參考：
- 整合測試報告: `docs/integration-test-report.md`
- 部署指南: `docs/`
- 故障排除: 運行 `python scripts/test_integration.py --mode debug` 進行診斷
