# 家用智慧助理系統 (Smart Home Assistant)

一個全功能的智能家庭管理平台，幫助家庭成員管理日常活動、追蹤家用耗材更換時間，並支持多種智能家居功能擴展。

## 功能特點

- **家庭行事曆**: 集中管理全家人的行程與活動
- **耗材管理**: 智能追蹤家用耗材（如濾水器、空氣清淨機濾網）的更換週期，自動提醒
- **智能裝置控制**: 整合多種智能家電，實現集中管理 (TBD)
- **能源監控**: 追蹤家庭能源使用情況，提供節能建議 (TBD)
- **多用戶支持**: 家庭成員角色與權限管理

## 技術堆疊

- **前端**: Angular 17
- **後端**: Python Flask RESTful API
- **資料庫**: 
  - 生產環境: Azure SQL Database (TBD)
  - 開發環境: PostgreSQL
- **部署**: Microsoft Azure 雲平台 (TBD)
- **容器化**: Docker & Docker Compose
- **認證授權**: OAuth 2.0 / JWT
- **即時通訊**: WebSocket / Socket.IO (TBD)
- **CI/CD**: GitHub Actions (TBD)

## 安裝與設置

### 前置需求

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose (推薦)

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
python scripts/init_local_db.py
python scripts/seed_test_data.py
```

#### 方法 2: 使用 Docker (推薦)

```bash
# 克隆專案
git clone https://github.com/yourusername/SmartHomeAssistantWeb.git
cd SmartHomeAssistantWeb

# 複製環境變數範本並根據需要修改
cp .env.example .env

# 啟動 Docker 容器
docker-compose up -d
```

### 啟動應用

#### 不使用 Docker

```bash
# 啟動後端
cd backend
source venv/bin/activate  # Windows 使用: venv\Scripts\activate
flask run --debug

# 另開終端啟動前端
cd frontend
ng serve --open
```

訪問: http://localhost:4200

#### 使用 Docker

Docker Compose 啟動後訪問: http://localhost:4200

## 專案結構

```
SmartHomeAssistantWeb/
├── frontend/               # Angular 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # UI 組件
│   │   │   ├── pages/      # 頁面組件
│   │   │   ├── models/     # 資料模型定義
│   │   │   ├── services/   # 服務層
│   │   │   ├── guards/     # 路由守衛
│   │   │   ├── interceptors/ # HTTP 請求攔截器
│   │   │   └── shared/     # 共用元素
│   │   ├── assets/         # 靜態資源
│   │   └── environments/   # 環境配置
│   ├── tests/              # 單元測試
│   └── e2e/                # E2E 測試 (TBD)
├── backend/                # Python Flask 後端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 資料模型
│   │   ├── services/       # 業務邏輯層
│   │   ├── schemas/        # 資料驗證結構
│   │   └── utils/          # 工具函數
│   ├── migrations/         # 資料庫遷移腳本
│   ├── tests/              # 單元測試 (TBD)
│   └── scripts/            # 實用腳本
├── docker/                 # Docker 配置
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml (TBD)
│   ├── frontend/Dockerfile
│   └── backend/Dockerfile
├── infrastructure/         # Azure 部署配置 (TBD)
│   ├── terraform/          # IaC 配置 (TBD)
│   └── azure-pipelines/    # CI/CD 配置 (TBD)
├── docs/                   # 專案文件 (TBD)
└── scripts/                # 項目管理腳本
```

## 開發指南

### 分支管理策略

- `main`: 生產環境分支，只接受經過審核的 PR
- `develop`: 開發分支，新功能整合到此分支
- `feature/*`: 功能分支，從 develop 分支出
- `hotfix/*`: 緊急修復分支，從 main 分支出

### 前端開發

- 遵循 Angular 風格指南
- 使用 TypeScript 強型別
- 組件使用特性模組組織
- 使用 NgRx 進行狀態管理 (TBD)
- 使用 Angular Material 組件庫

### 後端開發

- 遵循 RESTful API 設計原則
- 使用 Flask-SQLAlchemy 進行數據庫操作
- 使用 Marshmallow 進行數據序列化/驗證 (TBD)
- 遵循 PEP 8 代碼風格

## 主要功能模塊

### 1. 家庭行事曆

- 支援多用戶共享
- 行程提醒通知
- 重複行程設置
- 行程分類與標記
- 導出/導入日曆功能 (TBD)

### 2. 耗材管理

- 耗材到期提醒
- 自定義更換週期
- 更換歷史記錄
- 耗材庫存追蹤
- QR Code 掃描識別 (TBD)

### 3. 智能裝置整合 (TBD)

- 支援主流智能家電品牌 (TBD)
- 設備自動發現功能 (TBD)
- 場景模式設定 (TBD)
- 用戶自定義自動化規則 (TBD)
- 語音助手整合 (TBD)

## 部署指南

### Azure 部署 (TBD)

專案使用 Terraform 管理 Azure 資源，部署流程透過 Azure Pipelines 自動化。

```bash
cd infrastructure/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### 環境變數配置

部署前請確保已正確設置以下環境變數：

```bash
# Azure 基本設定 (TBD)
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id

# 資料庫連線
DB_HOST=your-db-server.database.windows.net
DB_NAME=homeassistant
DB_USER=dbadmin
DB_PASSWORD=your-secure-password

# 應用設定
JWT_SECRET_KEY=your-secure-jwt-key
SMTP_SERVER=smtp.yourdomain.com (TBD)
SMTP_PORT=587 (TBD)
```

## 故障排除

### Docker 環境中的數據庫連接問題

如果遇到 `ConnectionRefusedError: [Errno 111] Connect call failed ('172.21.0.2', 5432)` 錯誤，請檢查：

1. 確保 PostgreSQL 容器已正確啟動：
```bash
docker-compose ps
```

2. 檢查環境變數配置是否正確。在 docker-compose.yml 中確保以下設置：
```yaml
backend:
  environment:
    - DATABASE_URL=postgresql://postgres:password@db:5432/homeassistant
  depends_on:
    - db
    - condition: service_healthy  # 確保等待資料庫就緒
```

3. 檢查資料庫健康狀態：
```bash
docker-compose exec db pg_isready
```

4. 如果問題持續，嘗試重新啟動服務：
```bash
docker-compose down
docker volume prune  # 小心!這會刪除未使用的數據卷
docker-compose up --build
```

### 前端構建問題

如果遇到前端構建錯誤：

1. 檢查 Node.js 版本兼容性：
```bash
node -v  # 確保版本 >= 18.0.0
```

2. 清理 npm 緩存：
```bash
npm cache clean --force
rm -rf node_modules
npm install
```

3. 確保 Angular CLI 版本正確：
```bash
ng version
```

4. 如果遇到 Angular AOT 編譯錯誤，請檢查：
   - 組件模板中的綁定語法
   - 循環依賴問題
   - TypeScript 類型註解

### 常見的 JWT 認證問題

1. Token 過期：確保前後端時間同步，檢查 token 過期時間設置
2. CORS 問題：檢查後端 CORS 配置是否正確
3. 刷新 token 機制失效：檢查刷新流程實現

### 開發環境 HTTPS 設置 (TBD)

為本地開發環境設置 HTTPS：

1. 生成自簽證書：
```bash
cd scripts
./generate-local-certs.sh  # Windows 使用 generate-local-certs.bat
```

2. 更新前端配置：
```bash
ng serve --ssl --ssl-cert "./ssl/server.crt" --ssl-key "./ssl/server.key"
```

3. 更新後端配置：
```python
# 在 app/__init__.py 中
app.run(ssl_context=('ssl/server.crt', 'ssl/server.key'))
```

## 授權

MIT License

## 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

### 提交規範

請遵循語義化提交信息規範：
- `feat:` 新功能
- `fix:` 錯誤修復
- `docs:` 文檔更新
- `style:` 代碼風格調整
- `refactor:` 重構
- `test:` 測試相關
- `chore:` 構建過程或輔助工具變動

## 聯絡資訊

- **專案維護者**: Your Name
- **Email**: your.email@example.com
- **問題回報**: [Issue Tracker](https://github.com/yourusername/SmartHomeAssistantWeb/issues)
- **討論群組**: [Discussions](https://github.com/yourusername/SmartHomeAssistantWeb/discussions) (TBD)

---

感謝您對家用智慧助理系統的關注與支持！
