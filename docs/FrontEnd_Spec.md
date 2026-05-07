# Frontend 規格文件

## 技術棧

- **框架**: Angular 17 + TypeScript
- **架構**: NgModule（非 standalone components）
- **表單**: ReactiveFormsModule（`FormBuilder` + `FormGroup`）
- **HTTP**: `HttpClient`（透過 Service 封裝，元件不直接使用）
- **樣式**: SCSS（各元件獨立 `.scss`，全域在 `src/styles.scss`）
- **端口**: 4200（開發/Debug）

---

## 目錄結構

```
frontend/src/app/
├── app.module.ts
├── app-routing.module.ts
├── pages/
│   ├── dashboard/          # 儀表板
│   ├── schedule/           # 行程管理
│   └── consumable/         # 耗材管理
├── shared/
│   ├── models/             # TypeScript interface
│   ├── services/           # HttpClient 封裝服務
│   └── components/         # 共用元件（header、sidebar、calendar、loading-spinner）
└── environments/
    ├── environment.ts       # 開發環境設定
    └── environment.prod.ts  # 生產環境設定
```

---

## 開發規範

- 所有元件在 `AppModule` 的 `declarations` 宣告
- 共用介面放在 `shared/models/`
- Service 放在 `shared/services/`，以 `providedIn: 'root'` 注入
- API URL 從 `environment.apiUrl` 讀取，不寫死
- 元件 selector 前綴 `app-`
- 命名規則：TypeScript camelCase

---

## 新增功能頁面標準流程

1. 在 `shared/models/` 新增 interface 檔案
2. 在 `shared/services/` 新增 Service
3. 在 `pages/` 新增頁面元件目錄
4. 在 `app.module.ts` 的 `declarations` 新增元件
5. 在 `app-routing.module.ts` 新增路由

---

## 頁面功能

### Dashboard

- 以月曆形式顯示行事曆，無論是否有行程資料都永久顯示
- 預設選中今天的日期
- 點擊日期顯示該日所有行程詳情
- 全域無行程或單日無行程時顯示友善提示和新增連結
- 點擊行程直接跳轉到編輯頁面

### Schedule（行程管理）

#### 雙檢視模式
- **月曆檢視**：月份導航、日期選擇、行程指示器（每日最多顯示 2 個，超過顯示 `+數量`）
- **列表檢視**：傳統行程列表
- 透過右上角按鈕切換

#### 互動功能
- 點擊月曆上的日期查看當日行程
- 點擊行程指示器直接編輯
- 選擇日期後新增行程自動填入該日期
- 今天按鈕快速返回

#### 月曆顏色說明
| 顏色 | 含義 |
|------|------|
| 藍色背景 | 今天的日期 |
| 深藍邊框 | 選中的日期 |
| 淺藍背景 | 有行程的日期 |
| 藍色指示器 | 行程標題 |

### Consumable（耗材管理）

- 顯示所有耗材及剩餘天數（由 Backend 計算回傳）
- 支援新增、編輯、刪除耗材
- 欄位：名稱、類別、安裝日期、使用期限（天）、備註

---

## 環境設定

```typescript
// environment.ts（開發）
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};

// environment.prod.ts（生產）
export const environment = {
  production: true,
  apiUrl: '/api'  // 透過 Nginx 代理
};
```
