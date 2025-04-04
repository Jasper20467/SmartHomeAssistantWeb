# 家用智慧助理系統

一個全功能的智能家庭管理平台，幫助家庭成員管理日常活動、追蹤家用耗材更換時間，並支持多種智能家居功能擴展。

## 功能特點

- **家庭行事曆**: 集中管理全家人的行程與活動
- **耗材管理**: 智能追蹤家用耗材（如濾水器、空氣清淨機濾網）的更換週期，自動提醒
- **可擴展架構**: 模組化設計，可輕鬆擴充新功能

## 技術堆疊

- **前端**: Angular 13
- **後端**: Python Flask
- **資料庫**: 
  - 生產環境: Azure SQL Database
  - 開發環境: SQLite/PostgreSQL
- **部署**: Microsoft Azure 雲平台
- **容器化**: Docker & Docker Compose

## 安裝與設置

### 前置需求

- Node.js 18+
- Python 3.9+
- Docker & Docker Compose (可選)

### 本地開發環境設置

#### 方法 1: 直接安裝

```bash
# 克隆專案
git clone https://github.com/yourusername/home-smart-assistant.git
cd home-smart-assistant

# 設置前端
cd frontend
npm install
cd ..

# 設置後端
cd backend
pip install -r requirements.txt

# 初始化資料庫
python scripts/init_local_db.py
python scripts/seed_test_data.py
```

#### 方法 2: 使用 Docker

```bash
# 克隆專案
git clone https://github.com/yourusername/home-smart-assistant.git
cd home-smart-assistant

# 啟動 Docker 容器
cd docker
docker-compose up
```

### 啟動應用

#### 不使用 Docker

```bash
# 啟動後端
cd backend
flask run

# 另開終端啟動前端
cd frontend
ng serve
```

訪問: http://localhost:4200

#### 使用 Docker

Docker Compose 啟動後訪問: http://localhost:4200

## 專案結構

```
home-smart-assistant/
├── frontend/               # Angular 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # 主要組件
│   │   │   ├── models/     # 資料模型
│   │   │   └── services/   # 服務層
│   │   └── environments/   # 環境配置
├── backend/                # Python Flask 後端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 資料模型
│   │   └── services/       # 服務層
│   └── scripts/            # 初始化腳本
├── docker/                 # Docker 配置
│   ├── docker-compose.yml
│   └── Dockerfiles
└── infrastructure/         # Azure 部署配置
```

## 開發指南

### 前端開發

- 遵循 Angular 風格指南
- 使用 TypeScript 強型別
- 組件放在對應功能目錄下

### 後端開發

- 遵循 RESTful API 設計原則
- 使用 Flask-SQLAlchemy 進行數據庫操作
- 遵循 PEP 8 代碼風格

## 主要功能模塊

### 1. 家庭行事曆

- 支援多用戶共享
- 行程提醒通知
- 重複行程設置
- 行程分類與標記

### 2. 耗材管理

- 耗材到期提醒
- 自定義更換週期
- 更換歷史記錄
- 耗材庫存追蹤

## 部署指南

### Azure 部署

專案使用 Terraform 管理 Azure 資源，部署流程透過 Azure Pipelines 自動化。

```bash
cd infrastructure/terraform
terraform init
terraform apply
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
```

3. 等待數據庫完全啟動：
```bash
docker-compose logs db
```

4. 如果問題持續，嘗試重新啟動服務：
```bash
docker-compose down
docker-compose up --build
```

### PostgreSQL 容器啟動信息說明

當看到以下日誌時，這是正常的啟動過程：
```
initdb: warning: enabling "trust" authentication for local connections
database system was shut down
database system is ready to accept connections
```

- `enabling "trust" authentication`: 這是 PostgreSQL 的默認安全設置提示，用於本地開發環境
- `database system was shut down`: 表示上次數據庫正常關閉
- `database system is ready`: 表示數據庫已完全啟動，可以接受連接

如果後端仍然無法連接，請確保：
1. 等待看到 "ready to accept connections" 消息後再訪問數據庫
2. 檢查後端服務的數據庫連接字符串是否正確

### 前端容器相關問題

當看到以下 npm 警告時，這不是錯誤而是依賴包的安全性提示：
```
frontend-1  | 4 moderate severity vulnerabilities
frontend-1  | To address all issues (including breaking changes), run:
frontend-1  |   npm audit fix --force
```

處理方法：
1. 如果在開發環境，可以暫時忽略這些警告
2. 要解決這些安全性問題，請在 frontend 目錄執行：
```bash
# 在容器內執行
docker-compose exec frontend npm audit fix

# 或在本地執行
cd frontend
npm audit fix
```
3. 如果容器退出，檢查是否已正確設置環境變數：
```yaml
frontend:
  environment:
    - NODE_ENV=development
```

4. 前端容器退出（exit code 0）：
```
frontend-1 exited with code 0
```
這表示容器正常完成了指令但沒有持續運行。這通常是因為 docker-compose.yml 中的指令設定問題。解決方法：

```yaml
# 在 docker-compose.yml 中確保前端容器有正確的啟動命令
frontend:
  command: npm start   # 或 ng serve --host 0.0.0.0
```

另外，確保 Dockerfile 中有正確的 CMD 指令：

```dockerfile
# 在前端的 Dockerfile 中
CMD ["npm", "start"]  # 或 ["ng", "serve", "--host", "0.0.0.0"]
```

## 授權

MIT License

## 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

---

如有問題或建議，歡迎開 Issue 或直接聯繫專案維護者。
