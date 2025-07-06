# Docker Images 推送腳本使用說明

## 概述
本專案提供了多個腳本來自動化建置和推送 Docker 映像到 Docker Hub，支援 Smart Home Assistant 的三個主要服務：frontend、backend 和 linebot。

## 腳本說明

### 1. `push_docker_images.ps1` - 完整功能版本

**功能特點：**
- 完整的錯誤檢查和驗證
- 彩色輸出和詳細進度顯示
- 自動備份和更新配置檔案
- 支援清理舊映像
- 詳細的執行報告

**使用方法：**
```powershell
# 推送特定版本
.\scripts\push_docker_images.ps1 1.1

# 推送 latest 版本
.\scripts\push_docker_images.ps1 latest

# 不指定版本（默認為 latest）
.\scripts\push_docker_images.ps1
```

### 2. `quick_push.ps1` - 快速推送版本

**功能特點：**
- 簡化的操作流程
- 自動生成時間戳版本號
- 快速建置和推送
- 適合日常開發使用

**使用方法：**
```powershell
# 使用自動生成的時間戳版本號 (例如: 2025.07.06.1200)
.\scripts\quick_push.ps1

# 指定版本號
.\scripts\quick_push.ps1 1.2
```

### 3. `push_docker_images.sh` - Linux/Mac 版本

**功能特點：**
- 與 PowerShell 版本功能相同
- 適用於 Linux 和 macOS 環境
- 支援 Bash 腳本

**使用方法：**
```bash
# 給予執行權限
chmod +x scripts/push_docker_images.sh

# 推送特定版本
./scripts/push_docker_images.sh 1.1

# 推送 latest 版本
./scripts/push_docker_images.sh latest
```

## 前置需求

### 1. Docker 環境
```powershell
# 檢查 Docker 是否安裝
docker --version

# 檢查 Docker 是否運行
docker info
```

### 2. Docker Hub 登入
```powershell
# 登入 Docker Hub
docker login

# 驗證登入狀態
docker info | Select-String "Username"
```

### 3. 必要檔案檢查
確保以下檔案存在：
- `docker/frontend.Dockerfile`
- `docker/backend.Dockerfile`
- `docker/linebot.Dockerfile`
- `frontend/` 目錄
- `backend/` 目錄
- `LineBotAI/` 目錄

## 映像配置

### 當前映像名稱
- **Frontend**: `popo510691/homeassistant.frontend`
- **Backend**: `popo510691/homeassistant.backend`
- **LineBot**: `popo510691/homeassistant.linebot`

### 版本標籤策略
- 每次推送都會創建指定版本的標籤
- 同時會更新 `latest` 標籤
- 建議使用語義化版本號（如 1.0.0, 1.1.0）

## 使用範例

### 場景 1：日常開發推送
```powershell
# 快速推送，自動生成時間戳版本
.\scripts\quick_push.ps1

# 輸出範例：
# 版本號: 2025.07.06.1200
# ✅ 成功: frontend, backend, linebot
```

### 場景 2：正式版本發布
```powershell
# 推送正式版本
.\scripts\push_docker_images.ps1 2.0.0

# 選擇性功能：
# - 清理舊映像：Y
# - 自動更新配置檔案：Y
```

### 場景 3：修復版本推送
```powershell
# 推送修復版本
.\scripts\push_docker_images.ps1 1.1.1

# 手動拉取最新映像
docker-compose pull
```

## 故障排除

### 常見問題

#### 1. Docker Hub 認證失敗
```
Error: unauthorized: authentication required
```
**解決方法：**
```powershell
docker logout
docker login
```

#### 2. 建置失敗
```
Error: failed to build
```
**檢查項目：**
- Dockerfile 語法是否正確
- 建置上下文是否存在
- 相依檔案是否完整

#### 3. 推送超時
```
Error: timeout
```
**解決方法：**
- 檢查網路連線
- 重試推送
- 使用較小的映像大小

#### 4. 權限不足
```
Error: access denied
```
**解決方法：**
- 確認 Docker Hub 帳號權限
- 檢查映像名稱是否正確

### 除錯技巧

#### 1. 查看建置日誌
```powershell
# 詳細建置日誌
docker build --progress=plain -f docker/frontend.Dockerfile ./frontend
```

#### 2. 測試單個映像
```powershell
# 只建置不推送
docker build -f docker/backend.Dockerfile -t test ./backend

# 本地測試
docker run --rm -p 8000:8000 test
```

#### 3. 檢查映像大小
```powershell
# 查看映像大小
docker images popo510691/homeassistant.*

# 清理未使用的映像
docker image prune
```

## 自動化配置更新

### AWS EC2 部署配置
腳本可以自動更新以下檔案的版本號：
- `scripts/DeployOn_AWS_Ec2/docker-compose_fromHub.yml`

### Azure Container Apps 配置
手動更新以下檔案：
- `scripts/DeployOn_Azure_ContainerApps/azure-docker-compose.yml`

## 最佳實踐

### 1. 版本管理
- 使用語義化版本號（Major.Minor.Patch）
- 開發版本使用時間戳
- 正式版本使用語義化版本

### 2. 建置優化
- 使用 `.dockerignore` 檔案
- 多階段建置減小映像大小
- 合併 RUN 指令減少層數

### 3. 安全性
- 定期更新基礎映像
- 掃描映像漏洞
- 使用非 root 用戶運行

### 4. 監控
- 定期檢查 Docker Hub 使用量
- 監控映像下載統計
- 設定自動建置觸發器

## 相關連結

- **Docker Hub Repository**: https://hub.docker.com/u/popo510691
- **Docker 官方文檔**: https://docs.docker.com/
- **Docker Hub 文檔**: https://docs.docker.com/docker-hub/
