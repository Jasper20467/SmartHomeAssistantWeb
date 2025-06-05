# 家用智慧助理系統 (Smart Home Assistant)

一個全功能的智能家庭管理平台，幫助家庭成員管理日常活動、追蹤家用耗材更換時間，並支持多種智能家居功能擴展。

---

## 功能特點

- **家庭行事曆**: 集中管理全家人的行程與活動
- **耗材管理**: 智能追蹤家用耗材（如濾水器、空氣清淨機濾網）的更換週期，自動提醒
- **智能裝置控制**: 整合多種智能家電，實現集中管理 (TBD)
- **能源監控**: 追蹤家庭能源使用情況，提供節能建議 (TBD)
- **多用戶支持**: 家庭成員角色與權限管理

---

## 技術堆疊

- **前端**: Angular 17
- **後端**: FastAPI
- **資料庫**: 
  - 生產環境: PostgreSQL
  - 開發環境: SQLite (Demo)
- **部署**: Docker & Docker Compose
- **即時通訊**: LINE Messaging API 整合
- **CI/CD**: Azure Pipelines

---

## 安裝與設置

### 前置需求

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose

### 本地開發環境設置

#### 方法 1: 直接安裝

```bash
# 克隆專案
git clone https://github.com/yourusername/SmartHomeAssistantWeb.git
cd SmartHomeAssistantWeb

# 設置前端
cd frontend
npm install
cd ..

# 設置後端
cd backend
python -m venv venv
source venv/bin/activate  # Windows 使用: venv\Scripts\activate
pip install -r requirements.txt

# 環境設定
cp .env.example .env
# 編輯 .env 檔案設定資料庫連線等資訊

# 初始化資料庫
python scripts/init_sqlite_demo_db.py
```

#### 方法 2: 使用 Docker (推薦)

```bash
# 克隆專案
git clone https://github.com/yourusername/SmartHomeAssistantWeb.git
cd SmartHomeAssistantWeb

# 複製環境變數範本並根據需要修改
cp .env.example .env

# 啟動 Docker 容器
docker-compose up --build
```

---

## 啟動應用

### 不使用 Docker

```bash
# 啟動後端
cd backend
source venv/bin/activate  # Windows 使用: venv\Scripts\activate
uvicorn app.main:app --reload

# 另開終端啟動前端
cd frontend
ng serve --open
```

訪問: http://localhost:4200

### 使用 Docker

Docker Compose 啟動後訪問: http://localhost:4200

---

## 專案結構

```
SmartHomeAssistantWeb/
├── frontend/               # Angular 前端
│   ├── src/
│   │   ├── app/            # 應用程式邏輯
│   │   ├── assets/         # 靜態資源
│   │   └── environments/   # 環境配置
├── backend/                # FastAPI 後端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 資料模型
│   │   ├── database/       # 資料庫初始化
│   │   └── main.py         # 主應用入口
├── LineBotAI/              # LINE Bot 整合
│   ├── services/           # 業務邏輯
│   ├── routes/             # 路由
│   └── app.py              # 主應用入口
├── docker/                 # Docker 配置
├── infrastructure/         # 部署配置
└── scripts/                # 實用腳本
```

---

## 開發指南

### 分支管理策略

- `main`: 生產環境分支
- `develop`: 開發分支
- `feature/*`: 功能分支
- `hotfix/*`: 緊急修復分支

### 前端開發

- 遵循 Angular 風格指南
- 使用 TypeScript 強型別
- 使用 Angular Material 組件庫

### 後端開發

- 遵循 RESTful API 設計原則
- 使用 SQLAlchemy 進行數據庫操作
- 遵循 PEP 8 代碼風格

---

## 部署指南

### 使用 Docker 部署

```bash
docker-compose -f docker-compose.yml up --build
```

### 部署至 Azure Container Apps

#### 前置準備

1. 安裝 Azure CLI 並登入
   ```powershell
   # 安裝 Azure CLI (如果尚未安裝)
   # 詳見: https://docs.microsoft.com/zh-tw/cli/azure/install-azure-cli

   # 登入 Azure
   az login
   ```

2. 確保已安裝 Azure CLI 容器應用擴充功能
   ```powershell
   az extension add --name containerapp --upgrade
   ```

3. 確保您已建立一個 Azure Container Registry (ACR)
   ```powershell
   # 建立資源群組（若不存在）
   az group create --name JYSmartHomeAssistant --location eastasia

   # 建立 Container Registry（若不存在）
   az acr create --resource-group JYSmartHomeAssistant --name jasperbasicacr --sku Basic
   ```

4. 登入 ACR 並獲取密碼
   ```powershell
   az acr login --name jasperbasicacr
   $acrPassword = az acr credential show --name jasperbasicacr --query "passwords[0].value" -o tsv
   ```

#### 建置與推送 Docker 映像檔

1. 建置映像檔並標記為生產環境版本
   ```powershell
   # 建置前端映像檔
   docker build -f ./docker/frontend.Dockerfile -t jasperbasicacr.azurecr.io/smarthomeassistantweb-frontend:1.0 ./frontend

   # 建置後端映像檔
   docker build -f ./docker/backend.Dockerfile -t jasperbasicacr.azurecr.io/smarthomeassistantweb-backend:1.0 ./backend

   # 建置資料庫映像檔
   docker build -t jasperbasicacr.azurecr.io/smarthomeassistantweb-db:1.0 -f ./docker/postgres.Dockerfile .
   ```

2. 推送映像檔到 ACR
   ```powershell
   docker push jasperbasicacr.azurecr.io/smarthomeassistantweb-frontend:1.0
   docker push jasperbasicacr.azurecr.io/smarthomeassistantweb-backend:1.0
   docker push jasperbasicacr.azurecr.io/smarthomeassistantweb-db:1.0
   ```

#### 部署至 Azure Container Apps

使用提供的部署腳本：
```powershell
# 移動到基礎設施目錄
cd infra

# 執行部署腳本
./deploy.ps1 -resourceGroupName "JYSmartHomeAssistant" -location "eastasia" -appName "JYHomeAssistant" -acrName "jasperbasicacr" -acrPassword $acrPassword -dbPassword "YourSecureDbPassword" -imageTag "1.0"
```

部署完成後，腳本將顯示應用程式的 URL。

#### 重要說明

- 前端應用在 Azure Container Apps 環境中使用 HTTP 埠 80（而非開發環境的 4200）
- NGINX 已配置為支援 Angular 的客戶端路由，避免 404 錯誤
- NGINX 同時配置了反向代理，將 `/api` 請求轉發到後端服務
- 後端 API 已啟用 CORS，支援跨域請求
- 前端環境配置已針對生產環境進行優化
- 所有服務間通信已配置在同一 Azure Container Apps 環境內
- 資料庫資料將持久化在 Azure 管理的存儲中
- LineBot 元件在目前設定中已被暫時禁用

---

## 故障排除

### Angular 路由在 NGINX 環境中的 404 問題

在生產環境中，Angular 的客戶端路由可能會導致 404 錯誤，因為 NGINX 預設會嘗試查找與 URL 路徑匹配的文件。解決方法：

1. 已在 `docker/nginx.conf` 中配置了 NGINX，使其支援 Angular 的客戶端路由：
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

2. 此配置確保所有路由都回退到 index.html，讓 Angular 路由接管導航。

3. 如果仍然出現問題，可手動重建並部署：
```bash
docker build -f ./docker/frontend.Dockerfile -t frontend ./frontend
docker run -p 80:80 frontend
```

### CORS 相關問題

如遇到 CORS（跨域資源共享）問題，通常表現為 API 請求返回 307 重定向或 OPTIONS 請求返回 400 錯誤：

1. 後端已配置 CORS 中間件，允許來自多個來源的請求：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:80", "http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. 前端 NGINX 配置已設置反向代理，將 API 請求轉發到後端：
```nginx
location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    # ... 其他代理設置 ...
}
```

3. 如果仍有 CORS 問題，可檢查：
   - 瀏覽器控制台錯誤信息
   - 後端日誌中的詳細錯誤
   - 確保 API 請求 URL 與環境配置匹配

### Docker 環境中的數據庫連接問題

1. 確保 PostgreSQL 容器已正確啟動：
```bash
docker-compose ps
```

2. 檢查環境變數配置是否正確。

3. 如果問題持續，嘗試重新啟動服務：
```bash
docker-compose down
docker-compose up --build
```

---

## 授權

MIT License

---

## 聯絡資訊

- **專案維護者**: Your Name
- **Email**: your.email@example.com
- **問題回報**: [Issue Tracker](https://github.com/yourusername/SmartHomeAssistantWeb/issues)
