# Azure Container Apps 命名慣例指南

## 命名規則要求

Azure Container Apps 的命名規則要求：
- 必須使用小寫字母數字或連字符 `-`
- 必須以字母開頭，以字母或數字結尾
- 不能包含連續連字符 `--`
- 長度必須在 2-32 個字符之間

## 修改摘要

以下是為符合 Azure Container Apps 命名慣例所做的修改：

1. 更新了 `main.bicep` 文件：
   - 將 `appName` 參數默認值從 `JYHomeAssistant` 改為 `jyhomeassistant`
   - 使用 `toLower()` 函數確保所有資源名稱都是小寫的

2. 更新了 `main-acr-template.bicep` 文件：
   - 將 `appName` 參數默認值從 `JYHomeAssistant` 改為 `jyhomeassistant`
   - 使用 `toLower()` 函數確保所有資源名稱都是小寫的

3. 更新了部署腳本：
   - `deploy_new.ps1` 中的參數默認值改為小寫
   - `deploy_with_acr.ps1` 中的參數默認值改為小寫
   - `github-workflow-template.yml` 中的環境變數改為小寫

4. 更新了 README.md：
   - 所有部署命令示例使用小寫應用名稱
   - 添加了命名規則說明和故障排除指南

## 錯誤示例

部署使用大寫字母的應用名稱可能導致以下錯誤：
```
InvalidTemplateDeployment - The template deployment 'main' is not valid according to the validation procedure.
ValidationForResourceFailed - Validation failed for a resource.
ContainerAppInvalidName - Invalid ContainerApp name 'JYHomeAssistant-frontend'. A name must consist of lower case alphanumeric characters or '-', start with an alphabetic character, and end with an alphanumeric character and cannot have '--'.
```

## 最佳實踐

為避免命名相關問題：
1. 始終使用小寫字母命名 Azure 資源
2. 在 Bicep/ARM 模板中使用 `toLower()` 函數確保名稱合規
3. 避免使用特殊字符和連續連字符
4. 在部署前檢查所有資源名稱是否符合 Azure 命名慣例
