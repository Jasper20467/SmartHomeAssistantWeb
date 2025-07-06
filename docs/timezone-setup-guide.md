# 時區設定指南

## 概述
在 AWS EC2 上使用 Docker 部署 Smart Home Assistant 時，正確的時區設定非常重要，特別是對於行程管理功能。

## 為什麼需要時區設定？

### 1. 數據一致性
- **資料庫時間戳記**：確保所有時間戳記都使用一致的時區
- **行程排程**：確保行程時間顯示正確
- **日誌記錄**：方便追蹤和調試

### 2. 用戶體驗
- **前端顯示**：確保用戶看到的時間是本地時間
- **API 響應**：確保 API 返回的時間格式正確
- **排程功能**：確保自動化任務在正確時間執行

## 時區設定方法

### 1. 主機系統時區設定

#### Ubuntu/Debian 系統：
```bash
# 查看當前時區
timedatectl status

# 設定時區為台北時間
sudo timedatectl set-timezone Asia/Taipei

# 驗證設定
timedatectl status
```

#### CentOS/RHEL 系統：
```bash
# 查看當前時區
timedatectl status

# 設定時區為台北時間
sudo timedatectl set-timezone Asia/Taipei

# 或者使用傳統方法
sudo ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime
```

### 2. Docker 容器時區設定

#### 方法 1：環境變數設定
```yaml
environment:
  - TZ=Asia/Taipei
```

#### 方法 2：掛載時區檔案
```yaml
volumes:
  - /etc/timezone:/etc/timezone:ro
  - /etc/localtime:/etc/localtime:ro
```

#### 方法 3：Dockerfile 內設定
```dockerfile
# 對於 Alpine 基礎映像
RUN apk add --no-cache tzdata
ENV TZ=Asia/Taipei
RUN cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && echo "Asia/Taipei" > /etc/timezone

# 對於 Debian/Ubuntu 基礎映像
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```

### 3. 資料庫時區設定

#### PostgreSQL 設定：
```yaml
environment:
  - TZ=Asia/Taipei
  - PGTZ=Asia/Taipei
```

#### 在 SQL 中檢查時區：
```sql
SHOW timezone;
SELECT now();
```

## 驗證時區設定

### 1. 檢查容器時區
```bash
# 檢查容器內的時間
docker exec <container_name> date

# 檢查容器內的時區設定
docker exec <container_name> cat /etc/timezone
```

### 2. 檢查應用程式時區
```bash
# 檢查 Python 應用程式的時區
docker exec <backend_container> python -c "import datetime; print(datetime.datetime.now())"

# 檢查資料庫時區
docker exec <db_container> psql -U postgres -d smarthome -c "SELECT now();"
```

## 最佳實踐

### 1. 統一時區設定
- 所有服務（frontend、backend、database）都使用相同的時區
- 建議使用 Asia/Taipei 作為台灣地區的標準時區

### 2. 程式碼中的時區處理
```python
# Python 後端
import pytz
from datetime import datetime

# 使用 UTC 儲存，顯示時轉換為本地時區
utc_time = datetime.now(pytz.UTC)
local_time = utc_time.astimezone(pytz.timezone('Asia/Taipei'))
```

```typescript
// TypeScript 前端
// 使用 Date 物件處理時區
const now = new Date();
const localTime = now.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' });
```

### 3. 環境變數管理
```bash
# .env 檔案
TZ=Asia/Taipei
POSTGRES_TZ=Asia/Taipei
```

## 常見問題排除

### 1. 時間顯示不正確
- 檢查主機系統時區設定
- 檢查容器內時區設定
- 確認應用程式時區邏輯

### 2. 資料庫時間戳記錯誤
- 檢查 PostgreSQL 時區設定
- 確認連接字串中的時區參數
- 檢查資料庫連接時的時區設定

### 3. 前端時間顯示錯誤
- 確認瀏覽器時區設定
- 檢查 JavaScript 時區處理邏輯
- 確認 API 響應的時間格式

## 部署後檢查清單

- [ ] 主機系統時區設定正確
- [ ] 所有容器時區設定一致
- [ ] 資料庫時區設定正確
- [ ] 應用程式時區邏輯正確
- [ ] 前端時間顯示正確
- [ ] 日誌時間戳記正確

## 相關檔案

- `docker-compose.yml` - 包含時區設定的 Docker Compose 配置
- `docker-compose_fromHub.yml` - AWS EC2 部署用的 Docker Compose 配置
- `deploy_with_timezone.sh` - 包含時區檢查的部署腳本
- `frontend.Dockerfile` - 前端容器的時區設定
- `backend.Dockerfile` - 後端容器的時區設定
- `linebot.Dockerfile` - LineBot 容器的時區設定

## 更多資源

- [Docker 官方時區文檔](https://docs.docker.com/engine/reference/builder/#env)
- [PostgreSQL 時區文檔](https://www.postgresql.org/docs/current/datatype-datetime.html#DATATYPE-TIMEZONES)
- [Linux 時區設定指南](https://linuxize.com/post/how-to-set-or-change-timezone-in-linux/)
