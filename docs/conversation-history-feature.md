# 對話歷史功能示例

## 功能說明

ChatGPT 服務現在支援保持前五輪對話的歷史記錄，讓 LINE Bot 能夠進行上下文對話。

## 新功能

### 1. 對話歷史記錄
- 每個用戶獲得獨立的對話歷史
- 自動保存最近 5 輪對話
- 包含用戶訊息和 GPT 回應

### 2. 上下文理解
- GPT 能夠理解對話上下文
- 支援代名詞引用（如"它"、"那個"、"前面提到的"）
- 多輪對話邏輯連貫

## 對話範例

### 範例 1：排程管理的多輪對話
```
用戶: "這週六中午和朋友吃飯"
機器人: "已為您建立7月12日中午的聚餐排程。"

用戶: "改成晚上7點"
機器人: [理解是要修改剛才的排程] "已更新您的聚餐排程到晚上7點。"

用戶: "取消它"
機器人: [理解"它"指的是剛才的聚餐排程] "已為您取消7月12日的聚餐排程。"
```

### 範例 2：上下文引用
```
用戶: "查看這週六的排程"
機器人: [顯示排程列表]

用戶: "刪除第一個"
機器人: [理解是要刪除列表中的第一個排程] "已刪除指定的排程。"
```

## 技術實作

### 1. 對話歷史結構
```python
{
    "user_message": "用戶訊息",
    "gpt_response": {"action": "...", "reply": "..."},
    "timestamp": "2025-07-08T10:30:00Z"
}
```

### 2. 用戶識別
- 使用 LINE 用戶 ID 作為唯一識別
- 每個用戶擁有獨立的對話歷史
- 支援多用戶同時對話

### 3. 歷史管理
- 自動清理超過 5 輪的舊對話
- 提供手動清除歷史的方法
- 記錄對話時間戳

## API 更新

### ChatGPTService.process_message()
```python
# 舊版本
response = chatgpt_service.process_message(user_message)

# 新版本 - 支援 user_id
response = chatgpt_service.process_message(user_message, user_id)
```

### LineService.process_user_message()
```python
# 新版本自動從 LINE 事件提取 user_id
line_service.process_user_message(user_message, reply_token, chatgpt_service, user_id)
```

## 額外功能

### 查看對話歷史
```python
history = chatgpt_service.get_conversation_history(user_id)
```

### 清除對話歷史
```python
chatgpt_service.clear_conversation_history(user_id)
```

### 獲取對話摘要
```python
summary = chatgpt_service.get_conversation_summary()
```

## 注意事項

1. **記憶體使用**: 對話歷史存儲在記憶體中，重啟服務會清除所有歷史
2. **隱私考量**: 對話歷史包含用戶訊息，請注意隱私保護
3. **性能影響**: 每次請求會包含歷史對話，可能增加 token 使用量

## 未來改進

1. 持久化存儲（資料庫）
2. 自動歷史壓縮和摘要
3. 更智能的上下文理解
4. 用戶自定義歷史長度
