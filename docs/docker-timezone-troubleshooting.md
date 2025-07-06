# Docker 時區設定故障排除指南

## 問題描述
在 AWS EC2 上使用 Docker Compose 部署時，可能遇到以下時區相關錯誤：

```
Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/etc/timezone" to rootfs at "/etc/timezone": create mountpoint for /etc/timezone mount: cannot create subdirectories in "/var/lib/docker/overlay2/...": not a directory: unknown
```

## 問題原因
1. **檔案不存在**：主機系統上不存在 `/etc/timezone` 或 `/etc/localtime` 檔案
2. **檔案類型不匹配**：嘗試將檔案掛載到目錄，或將目錄掛載到檔案
3. **權限問題**：Docker 無法存取時區檔案
4. **系統差異**：不同 Linux 發行版的時區檔案結構不同

## 解決方案

### 方案 1：使用 Dockerfile 內建時區設定（推薦）

我們已經更新了所有 Dockerfile 來包含時區設定：

#### Frontend Dockerfile (Alpine 基礎)
```dockerfile
FROM nginx:alpine

# Install timezone data
RUN apk add --no-cache tzdata

# Set timezone to Asia/Taipei
ENV TZ=Asia/Taipei
RUN cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && echo "Asia/Taipei" > /etc/timezone
```

#### Backend Dockerfile (Python 基礎)
```dockerfile
FROM python:3.10

# Install timezone data and set timezone
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```

#### Docker Compose 配置
```yaml
services:
  frontend:
    environment:
      - TZ=Asia/Taipei
    # 移除 volumes 掛載
    
  backend:
    environment:
      - TZ=Asia/Taipei
    # 移除 volumes 掛載
    
  db:
    environment:
      - TZ=Asia/Taipei
      - PGTZ=Asia/Taipei
    # 移除 volumes 掛載
```

### 方案 2：條件式時區檔案掛載

如果您想保持檔案掛載方式，可以使用條件式掛載：

```yaml
services:
  app:
    environment:
      - TZ=Asia/Taipei
    volumes:
      # 只有當檔案存在時才掛載
      - ${HOST_TIMEZONE_FILE:-/dev/null}:/etc/timezone:ro
      - ${HOST_LOCALTIME_FILE:-/dev/null}:/etc/localtime:ro
```

### 方案 3：使用 init 容器設定時區

```yaml
services:
  timezone-init:
    image: busybox
    command: |
      sh -c "
        if [ ! -f /shared/timezone ]; then
          echo 'Asia/Taipei' > /shared/timezone
        fi
      "
    volumes:
      - timezone-data:/shared
      
  app:
    depends_on:
      - timezone-init
    environment:
      - TZ=Asia/Taipei
    volumes:
      - timezone-data:/etc:ro

volumes:
  timezone-data:
```

## 驗證時區設定

### 1. 檢查容器內時區
```bash
# 檢查容器內的時間
docker exec <container_name> date

# 檢查容器內的時區設定
docker exec <container_name> cat /etc/timezone 2>/dev/null || echo "No timezone file"
docker exec <container_name> ls -la /etc/localtime 2>/dev/null || echo "No localtime file"

# 檢查環境變數
docker exec <container_name> printenv TZ
```

### 2. 檢查 PostgreSQL 時區
```bash
# 連接到 PostgreSQL 並檢查時區
docker exec <db_container> psql -U postgres -d smarthome -c "SHOW timezone; SELECT now();"
```

### 3. 檢查 Python 應用程式時區
```bash
# 檢查 Python 的時區設定
docker exec <backend_container> python -c "
import datetime
import os
print(f'TZ env var: {os.environ.get(\"TZ\", \"Not set\")}')
print(f'Current time: {datetime.datetime.now()}')
print(f'UTC time: {datetime.datetime.utcnow()}')
"
```

## 最佳實踐

### 1. 統一使用環境變數方式
```yaml
environment:
  - TZ=Asia/Taipei
```

### 2. 在 Dockerfile 中預設時區
```dockerfile
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```

### 3. 避免檔案掛載
- 不要掛載 `/etc/timezone` 和 `/etc/localtime`
- 使用環境變數和 Dockerfile 設定

### 4. 使用官方映像檔的時區支援
- PostgreSQL：支援 `TZ` 和 `PGTZ` 環境變數
- Node.js：支援 `TZ` 環境變數
- Python：支援 `TZ` 環境變數

## 常見問題

### Q1: 為什麼移除了時區檔案掛載？
A1: 因為不同系統的時區檔案結構不同，檔案掛載容易出現問題。使用 Dockerfile 內建設定更穩定。

### Q2: 如何確認時區設定生效？
A2: 使用 `docker exec <container> date` 檢查容器內時間，或查看應用程式日誌中的時間戳記。

### Q3: 資料庫時區設定不正確怎麼辦？
A3: 確保設定了 `TZ` 和 `PGTZ` 環境變數，並重啟容器。

### Q4: 如何處理夏令時間？
A4: 使用 `Asia/Taipei` 時區會自動處理夏令時間（雖然台灣目前不實施夏令時間）。

## 部署檢查清單

- [ ] 更新所有 Dockerfile 包含時區設定
- [ ] 移除 Docker Compose 中的時區檔案掛載
- [ ] 設定環境變數 `TZ=Asia/Taipei`
- [ ] 資料庫設定 `PGTZ=Asia/Taipei`
- [ ] 重新建置並部署容器
- [ ] 驗證所有容器的時區設定

## 更新的檔案

- `docker-compose.yml`：移除時區檔案掛載
- `scripts/DeployOn_AWS_Ec2/docker-compose_fromHub.yml`：移除時區檔案掛載
- `docker/frontend.Dockerfile`：添加時區設定
- `docker/backend.Dockerfile`：添加時區設定
- `docker/linebot.Dockerfile`：添加時區設定
- `scripts/DeployOn_AWS_Ec2/deploy_with_timezone.sh`：更新部署腳本
