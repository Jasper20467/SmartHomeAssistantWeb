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

本專案支持兩種 Docker 部署環境：本地 Docker Compose 和 Azure Container Apps。

#### 本地 Docker Compose 部署

```bash
docker-compose -f docker-compose.yml up --build
```

注意：在本地環境中，前端容器使用 Nginx 的本地配置，會自動通過 Docker 網絡解析 `backend` 服務名稱。

#### Azure Container Apps 部署

在 Azure 環境中，我們採用一個更靈活的配置方式：
- 使用 `BACKEND_URL` 環境變數來指定後端 API 的位置
- 入口點腳本會檢測環境，根據是否存在 `BACKEND_URL` 選擇正確的 Nginx 配置
- 這樣同一個容器映像可在本地和雲端環境下工作

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

3. 確保您已建立資源群組
   ```powershell
   # 建立資源群組（若不存在）
   az group create --name JYSmartHomeAssistant --location eastasia
   ```

#### Docker Hub vs Azure Container Registry 比較

| 特性 | Docker Hub | Azure Container Registry (ACR) |
|------|------------|------------------------------|
| 訪問控制 | 公開映像可被任何人下載 | 完全控制訪問權限，支持 Azure AD 整合 |
| 網絡延遲 | 可能較高 | 與 Azure 服務位於相同區域時延遲較低 |
| 費用 | 基本功能免費，高級功能付費 | 按層級收費（Basic、Standard、Premium） |
| 映像掃描 | 有限 | 內建漏洞掃描 |
| 地理複寫 | 無 | 支持（Premium 層級） |
| 適用情境 | 開發/測試、公開項目 | 生產環境、企業應用、敏感數據 |
| 部署複雜度 | 較簡單 | 需額外設置，但提供更多功能 |

#### 建置與推送 Docker 映像檔

##### 方法一：使用 Docker Hub（推薦）

已使用 Docker Hub 上的公共映像，不需要本地構建和推送：
   ```powershell
   # Docker Hub 映像資訊
   前端: popo510691/homeassistant.front:1.0
   後端: popo510691/homeassistant.backend:1.0
   資料庫: postgres:14
   ```

如需手動建置並推送到 Docker Hub：
   ```powershell
   # 建置前端映像檔
   docker build -f ./docker/frontend.Dockerfile -t popo510691/homeassistant.front:1.0 ./frontend

   # 建置後端映像檔
   docker build -f ./docker/backend.Dockerfile -t popo510691/homeassistant.backend:1.0 ./backend

   # 推送到 Docker Hub (需要先 docker login)
   docker push popo510691/homeassistant.front:1.0
   docker push popo510691/homeassistant.backend:1.0
   ```

##### 方法二：使用 Azure Container Registry（ACR）

如果您希望使用私有容器註冊表，可以使用 Azure Container Registry：

1. 創建 Azure Container Registry：
   ```powershell
   az acr create --resource-group JYSmartHomeAssistant --name <您的ACR名稱> --sku Basic
   ```

2. 登入 ACR：
   ```powershell
   az acr login --name <您的ACR名稱>
   ```

3. 構建並推送映像：
   ```powershell
   # 構建映像
   az acr build --registry <您的ACR名稱> --image smarthomeassistantweb-frontend:1.0 --file ./docker/frontend.Dockerfile ./frontend
   az acr build --registry <您的ACR名稱> --image smarthomeassistantweb-backend:1.0 --file ./docker/backend.Dockerfile ./backend

   # 或使用 Docker 指令構建並推送
   docker build -f ./docker/frontend.Dockerfile -t <您的ACR名稱>.azurecr.io/smarthomeassistantweb-frontend:1.0 ./frontend
   docker build -f ./docker/backend.Dockerfile -t <您的ACR名稱>.azurecr.io/smarthomeassistantweb-backend:1.0 ./backend
   
   docker push <您的ACR名稱>.azurecr.io/smarthomeassistantweb-frontend:1.0
   docker push <您的ACR名稱>.azurecr.io/smarthomeassistantweb-backend:1.0
   ```

#### 部署至 Azure Container Apps

##### 最新更新：Nginx 配置修復 (2025-06-05)

> **重要：** 我們已解決 Azure Container Apps 中前端容器崩潰的問題，該問題是由於 nginx 配置中使用了僅適用於 Docker Compose 的硬編碼後端主機名。主要變更：
> 
> 1. 創建了兩套 nginx 配置：
>    - 本地 Docker Compose 模式：使用服務名稱 `backend:8000` 解析
>    - Azure Container Apps 模式：使用 `BACKEND_URL` 環境變數
> 2. 添加了智能入點(entrypoint)腳本，可根據環境變數選擇正確的配置
> 3. 變更環境變數從 `API_URL` 到 `BACKEND_URL` 以更清晰表達用途
> 4. 更新了所有部署腳本和文檔以使用新的配置方式
> 5. 新增了排除 Azure Container Apps 問題的診斷腳本
>
> 如果前端容器仍然崩潰，請執行 `infra/troubleshoot_container_apps.ps1` 進行診斷與修復。

##### 使用 Docker Hub 映像部署（預設方式）

> **注意：** 錯誤 `UNAUTHORIZED: authentication required` 表示使用的 Docker Hub 映像 `popo510691/homeassistant.front:1.0` 為私有或不存在。在部署前，請先確認：
> 1. 這些映像存在且為公開的，或
> 2. 您已登入 Docker Hub 並有權限訪問這些映像，或
> 3. 使用您自己建立並推送的公開映像

使用提供的部署腳本：
```powershell
# 移動到基礎設施目錄
cd infra

# 先建立並推送自己的公開映像（使用最新的 Nginx 配置改動）
docker build -f ../docker/frontend.Dockerfile -t your-dockerhub-username/homeassistant.frontend:1.0 ../frontend
docker build -f ../docker/backend.Dockerfile -t your-dockerhub-username/homeassistant.backend:1.0 ../backend
docker push your-dockerhub-username/homeassistant.frontend:1.0
docker push your-dockerhub-username/homeassistant.backend:1.0

# 執行新的 Container Apps 部署腳本
./deploy_container_apps.ps1 -ResourceGroupName JYSmartHomeAssistant -AppName jyhomeassistant
./deploy.ps1 -resourceGroupName "JYSmartHomeAssistant" -location "eastasia" -appName "jyhomeassistant" -dbPassword "YourSecureDbPassword" -imageTag "1.0"
```

##### 使用 ACR 映像部署（使用專用部署腳本）

專案提供了 ACR 專用的部署腳本，可以直接使用：

```powershell
# 移動到基礎設施目錄
cd infra

# 使用 ACR 部署腳本
./deploy_with_acr.ps1 -resourceGroupName "JYSmartHomeAssistant" -location "eastasia" -appName "jyhomeassistant" -dbPassword "YourSecureDbPassword" -acrName "<您的ACR名稱>" -acrPassword "<您的ACR密碼>" -imageTag "1.0"
```

此腳本會自動：
1. 檢查 ACR 是否存在，如不存在可以選擇創建新的 ACR
2. 修改 Bicep 檔案以支持 ACR 認證和映像路徑
3. 部署到 Azure Container Apps 環境

如果您想手動修改 Bicep 文件，可以參考 `infra/main-acr-template.bicep` 作為範例。

部署完成後，腳本將顯示應用程式的 URL。

##### ACR 與 Container Apps 的進階整合

如果您的 ACR 和 Container Apps 位於同一資源組或訂閱中，可以設置託管身份來簡化認證流程：

1. 為 Container Apps 環境啟用系統託管身份：
   ```powershell
   az containerapp env update --name <環境名稱> --resource-group <資源組名稱> --enable-managed-identity
   ```

2. 授予 Container Apps 環境對 ACR 的存取權限：
   ```powershell
   az role assignment create --assignee <容器應用環境主體ID> --scope <ACR資源ID> --role AcrPull
   ```

3. 更新 Bicep 模板，使用託管身份而非密碼認證。

這種方法更安全，不需要在部署時提供 ACR 密碼。

#### 重要說明

- Azure Container Apps 命名規則：
  - 必須使用小寫字母數字或連字符 `-`
  - 必須以字母開頭，以字母或數字結尾
  - 不能包含連續連字符 `--`
  - 長度必須在 2-32 個字符之間
- 前端應用在 Azure Container Apps 環境中使用 HTTP 埠 80（而非開發環境的 4200）
- NGINX 已配置為支援 Angular 的客戶端路由，避免 404 錯誤
- NGINX 同時配置了反向代理，將 `/api` 請求轉發到後端服務
- 後端 API 已啟用 CORS，支援跨域請求
- 前端環境配置已針對生產環境進行優化
- 所有服務間通信已配置在同一 Azure Container Apps 環境內
- 資料庫資料將持久化在 Azure 管理的存儲中
- LineBot 元件在目前設定中已被暫時禁用

#### 使用 ACR 的詳細說明

##### ACR 映像命名慣例

當使用 Azure Container Registry (ACR) 時，映像命名格式如下：
```
<acr-name>.azurecr.io/<repository-name>:<tag>
```

在本專案中：
- `<acr-name>`: 您的 ACR 名稱，例如 `jyhomeassistantacr`
- `<repository-name>`: 建議使用 `smarthomeassistantweb-frontend` 和 `smarthomeassistantweb-backend`
- `<tag>`: 版本號，例如 `1.0`、`1.1` 或 `latest`

##### ACR 映像推送指令

```powershell
# 登入到您的 ACR
az acr login --name <您的ACR名稱>

# 構建映像
docker build -f ./docker/frontend.Dockerfile -t <您的ACR名稱>.azurecr.io/smarthomeassistantweb-frontend:1.0 ./frontend
docker build -f ./docker/backend.Dockerfile -t <您的ACR名稱>.azurecr.io/smarthomeassistantweb-backend:1.0 ./backend

# 推送映像
docker push <您的ACR名稱>.azurecr.io/smarthomeassistantweb-frontend:1.0
docker push <您的ACR名稱>.azurecr.io/smarthomeassistantweb-backend:1.0
```

##### 使用 ACR 任務自動構建

Azure Container Registry 還提供了自動構建功能，可以直接從源代碼構建映像：

```powershell
# 從源碼直接構建
az acr build --registry <您的ACR名稱> --image smarthomeassistantweb-frontend:1.0 --file ./docker/frontend.Dockerfile ./frontend
az acr build --registry <您的ACR名稱> --image smarthomeassistantweb-backend:1.0 --file ./docker/backend.Dockerfile ./backend
```

##### ACR 安全考量

為了增強安全性，建議：
- 使用 Azure AD 身份進行 ACR 認證而非管理員憑據
- 定期輪換 ACR 憑據
- 開啟 ACR 映像掃描功能檢測潛在漏洞
- 考慮使用地理複寫提高可用性（Premium 層級）

---

## 故障排除

### Azure Container Apps 故障排除

#### 前端容器崩潰問題："host not found in upstream 'backend'"

如果前端容器在 Azure Container Apps 中出現崩潰，並顯示 "host not found in upstream 'backend'" 錯誤：

1. 問題原因：Nginx 配置中使用的 `backend` 主機名在容器應用環境中無法解析
2. 解決方法：
   - 我們已修改 Nginx 配置，提供了兩種工作模式：
     - 本地 Docker Compose 模式：使用服務名稱 `backend:8000`
     - Azure Container Apps 模式：使用 `BACKEND_URL` 環境變數
   - 確保在 Azure Container Apps 中設置了正確的 `BACKEND_URL` 環境變數

使用故障排除腳本：
```powershell
cd infra
./troubleshoot_container_apps.ps1 -ResourceGroupName JYSmartHomeAssistant -AppName jyhomeassistant
```

此腳本會：
- 檢查前端和後端容器的狀態
- 顯示前端容器的日誌，幫助診斷問題
- 提供更新 BACKEND_URL 環境變數的選項
- 重啟前端容器應用使更改生效

#### 檢查容器日誌

若要查看容器的日誌：
```powershell
az containerapp logs show --resource-group JYSmartHomeAssistant --name jyhomeassistant-frontend
```

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

### Azure Container Apps 部署錯誤

#### 命名慣例問題

如果遇到以下錯誤：
```
InvalidTemplateDeployment - ContainerAppInvalidName - Invalid ContainerApp name. A name must consist of lower case alphanumeric characters or '-', start with an alphabetic character, and end with an alphanumeric character and cannot have '--'.
```

請確保：
1. 應用程式名稱 (`appName`) 使用小寫字母，例如 `jyhomeassistant` 而非 `JYHomeAssistant`
2. 所有資源名稱都遵循 Azure 命名慣例
3. 使用 `toLower()` 函數確保 Bicep 模板中的名稱都是小寫的

---

## CI/CD 整合

### GitHub Actions 自動部署

專案提供了 GitHub Actions 工作流程範本，支持自動化構建和部署到 Azure Container Apps:

1. 將 `infra/github-workflow-template.yml` 複製到專案的 `.github/workflows/` 目錄下
2. 在 GitHub 儲存庫的 Secrets 中設置以下變數:

   **Docker Hub 部署需要:**
   - `DOCKERHUB_USERNAME`: Docker Hub 用户名
   - `DOCKERHUB_TOKEN`: Docker Hub 存取令牌
   - `AZURE_CREDENTIALS`: Azure 服務主體憑據 (JSON 格式)
   - `DB_PASSWORD`: 資料庫密碼

   **ACR 部署需要:**
   - `ACR_NAME`: Azure Container Registry 名稱
   - `ACR_USERNAME`: ACR 用户名
   - `ACR_PASSWORD`: ACR 密碼
   - `AZURE_CREDENTIALS`: Azure 服務主體憑據 (JSON 格式)
   - `DB_PASSWORD`: 資料庫密碼

3. 在工作流程文件中設置 `REGISTRY_TYPE` 環境變量為 `dockerhub` 或 `acr`

工作流程會在每次推送到 `main` 分支或建立發行標籤 (`v*.*.*`) 時自動觸發，也可以手動觸發。

---

## 授權

MIT License

---

## 聯絡資訊

- **專案維護者**: Your Name
- **Email**: your.email@example.com
- **問題回報**: [Issue Tracker](https://github.com/yourusername/SmartHomeAssistantWeb/issues)
