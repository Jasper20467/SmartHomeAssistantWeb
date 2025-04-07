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

---

## 故障排除

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
