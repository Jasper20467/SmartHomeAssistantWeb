import requests
import logging
import os
import json
from collections import deque
from Home_assistant.client import HomeAssistantClient

from datetime import datetime, timezone, timedelta

# 取得當前 UTC 日期
now = datetime.now(timezone.utc)

# 格式化日期 (ISO 日期) 與星期
today_iso = now.strftime("%Y-%m-%d")
weekday_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday = weekday_map[now.weekday()]

now_tw = now + timedelta(hours=8)
today_iso = now_tw.strftime("%Y-%m-%d")
weekday = weekday_map[now_tw.weekday()]



class ChatGPTService:
    def __init__(self, api_key, backend_url=None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        # Initialize Home Assistant client for backend API calls
        self.backend_url = backend_url or os.getenv('BACKEND_API_URL', 'http://backend:8000')
        self.ha_client = HomeAssistantClient(self.backend_url)
        
        # 對話歷史記錄 - 使用字典來為每個用戶維護獨立的對話歷史
        self.conversation_histories = {}
        self.max_history_length = 5  # 保留最近 5 輪對話
        
        self.logger.info(f"ChatGPT service initialized with backend URL: {self.backend_url}")

    def _get_user_conversation_history(self, user_id: str):
        """獲取或創建用戶的對話歷史"""
        if user_id not in self.conversation_histories:
            self.conversation_histories[user_id] = deque(maxlen=self.max_history_length)
        return self.conversation_histories[user_id]

    def _add_to_conversation_history(self, user_id: str, user_message: str, gpt_response: dict):
        """添加對話到歷史記錄"""
        history = self._get_user_conversation_history(user_id)
        
        conversation_entry = {
            "user_message": user_message,
            "gpt_response": gpt_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        history.append(conversation_entry)
        self.logger.info(f"Added conversation to history for user {user_id}. History length: {len(history)}")

    def _build_conversation_context(self, user_id: str):
        """構建對話上下文"""
        history = self._get_user_conversation_history(user_id)
        
        if not history:
            return []
        
        context_messages = []
        
        for entry in history:
            # 添加用戶訊息
            context_messages.append({
                "role": "user",
                "content": entry["user_message"]
            })
            
            # 添加 GPT 回應 (只保留 reply 部分，避免 JSON 結構混亂)
            gpt_reply = entry["gpt_response"].get("reply", str(entry["gpt_response"]))
            context_messages.append({
                "role": "assistant",
                "content": gpt_reply
            })
        
        return context_messages

    def process_message(self, user_message, user_id=None):
        """Process user message using ChatGPT API with backend integration and conversation history"""
        # 如果沒有提供 user_id，使用預設值
        if user_id is None:
            user_id = "default_user"
            
        try:
            # First, try to get context from backend API
            context = self._get_backend_context(user_message)
            
            # Enhance the prompt with backend context
            enhanced_prompt = self._enhance_prompt(user_message, context)
            
            # Build conversation context from history
            conversation_context = self._build_conversation_context(user_id)
            
            # Call ChatGPT API
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 構建訊息序列：系統提示 + 對話歷史 + 當前訊息
            messages = [
                {
                    'role': 'system',
                    'content': (
                        "You are a smart home assistant integrated with a LINE Bot.\n"
                        f"Today's date is {today_iso} ({weekday}).\n"
                        "Time zone: UTC+8.\n\n"
                        "\n"
                        "Your role:\n"
                        "- Understand user messages in Chinese.\n"
                        "- If the message requires performing backend operations related to schedules or consumables, return a JSON object with the specific action and parameters.\n"
                        "- If the user is only chatting or asking general questions, return a JSON object with action:\"text_reply\" and provide the reply text.\n"
                        "- If the user request does not contain all required information (e.g., missing schedule ID), do not guess. Instead, return an action that helps retrieve or clarify the needed information and include a reply asking the user.\n"
                        "- Remember the conversation context and refer to previous messages when relevant.\n"
                        "\n"                            
                         "Important:\n"
                            "- If the user describes a new event with date and time, assume create_schedule by default, unless they clearly mention '查詢', '顯示', or '看看'.\n"
                            "- Only use get_schedule when the user explicitly asks to see or list schedules.\n"
                            "- Always respond with a valid JSON object.\n"
                            "- Dates must be in ISO 8601 format (e.g., 2025-07-08T12:00:00Z) if needed.\n"
                            "- Never guess IDs or date ranges.\n"
                            "- Remember the conversation context and refer to previous messages when relevant.\n"
                            "- Use conversation history to understand context and references (like 'it', 'that', 'the previous one').\n"
                            "- When the conversation context already includes schedule list information, and the user specifies which schedule to modify or delete (e.g., by ID or name), directly generate the corresponding update_schedule or delete_schedule action.\n"
                        "\n"
                        "Output format:\n"
                        "{\n"
                        "  \"action\": \"one of [create_schedule, get_schedule, update_schedule, delete_schedule, create_consumable, get_consumable, update_consumable, delete_consumable, text_reply]\",\n"
                        "  \"parameters\": { ... },\n"
                        "  \"reply\": \"text to show to user\"\n"
                        "}\n"
                        "\n"
                        "Examples:\n"
                        "\n"
                        "1) User says: \"這週六中午和朋友吃飯\"\n"
                        "Return:\n"
                        "{\n"
                        "  \"action\": \"create_schedule\",\n"
                        "  \"parameters\": {\n"
                        "    \"title\": \"和朋友吃飯\",\n"
                        "    \"description\": \"這週六中午聚餐\",\n"
                        "    \"start_time\": \"2025-07-12T12:00:00Z\"\n"
                        "  },\n"
                        "  \"reply\": \"已為您建立7月12日中午的聚餐排程。\"\n"
                        "}\n"
                        "\n"
                        "2) User says: \"把今天晨跑改成一小時\"\n"
                        "Return:\n"
                        "{\n"
                        "  \"action\": \"get_schedule\",\n"
                        "  \"parameters\": {\n"
                        "    \"date\": \"2025-07-08\"\n"
                        "  },\n"
                        "  \"reply\": \"請告訴我要修改哪一筆排程，請提供名稱或ID。\"\n"
                        "}\n"
                        "\n"
                        "3) User says: \"更新ID 2，改成一小時\"\n"
                        "Return:\n"
                        "{\n"
                        "  \"action\": \"update_schedule\",\n"
                        "  \"parameters\": {\n"
                        "    \"id\": 2,\n"
                        "    \"end_time\": \"2025-07-08T07:00:00Z\"\n"
                        "  },\n"
                        "  \"reply\": \"已更新ID 2的排程，時間已延長至一小時。\"\n"
                        "}\n"
                        "\n"
                        "4) User says: \"取消這週六的活動\"\n"
                        "Return:\n"
                        "{\n"
                        "  \"action\": \"get_schedule\",\n"
                        "  \"parameters\": {\n"
                        "    \"date\": \"2025-07-12\"\n"
                        "  },\n"
                        "  \"reply\": \"我找到7月12日的排程，請告訴我要取消哪一筆活動，請提供名稱或ID。\"\n"
                        "}\n"
                        "\n"
                        "5) User says: \"取消ID 3\"\n"
                        "Return:\n"
                        "{\n"
                        "  \"action\": \"delete_schedule\",\n"
                        "  \"parameters\": {\n"
                        "    \"id\": 3\n"
                        "  },\n"
                        "  \"reply\": \"已為您取消ID 3的排程。\"\n"
                        "}\n"
                        "\n"
                        "6) User says: \"目前有哪些消耗品？\"\n"
                        "Return:\n"
                        "{\n"
                        "  \"action\": \"get_consumable\",\n"
                        "  \"parameters\": {},\n"
                        "  \"reply\": \"正在查詢目前的消耗品...\"\n"
                        "}\n"
                        "\n"
                        "7) User says: \"你好！\"\n"
                        "Return:\n"
                        "{\n"
                        "  \"action\": \"text_reply\",\n"
                        "  \"reply\": \"你好！有什麼我可以幫忙的？\"\n"
                        "}\n"
                    )
                }
            ]
            
            # 添加對話歷史
            messages.extend(conversation_context)
            
            # 添加當前用戶訊息
            messages.append({
                'role': 'user',
                'content': enhanced_prompt
            })
            
            data = {
                'model': 'gpt-4.1-nano',
                'messages': messages,
                'max_tokens': 300
            }
            
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Try to parse JSON response
                try:
                    json_response = json.loads(content)
                    
                    # 將對話添加到歷史記錄
                    self._add_to_conversation_history(user_id, user_message, json_response)
                    
                    return json_response
                except json.JSONDecodeError:
                    # If not valid JSON, return as text reply
                    fallback_response = {
                        "action": "text_reply",
                        "reply": content
                    }
                    
                    # 將對話添加到歷史記錄
                    self._add_to_conversation_history(user_id, user_message, fallback_response)
                    
                    return fallback_response
            else:
                error_response = {
                    "action": "text_reply",
                    "reply": "Sorry, I couldn't generate a response."
                }
                
                # 將對話添加到歷史記錄
                self._add_to_conversation_history(user_id, user_message, error_response)
                
                return error_response
                
        except Exception as e:
            self.logger.error(f"ChatGPT API error: {e}")
            error_response = {
                "action": "text_reply",
                "reply": "Error processing message. Please try again."
            }
            
            # 將對話添加到歷史記錄
            self._add_to_conversation_history(user_id, user_message, error_response)
            
            return error_response

    def _get_backend_context(self, user_message):
        """Get relevant context from backend API"""
        context = {}
        
        try:
            # Try to get schedules if message relates to scheduling (Chinese and English keywords)
            schedule_keywords = ['schedule', 'appointment', 'reminder', 'time', '排程', '行程', '提醒', '時間', '預約', '會議']
            if any(keyword in user_message.lower() for keyword in schedule_keywords):
                schedules = self.ha_client.schedules.get_schedules()
                if schedules and not schedules.get('error'):
                    context['schedules'] = schedules
            
            # Try to get consumables if message relates to supplies (Chinese and English keywords)
            consumable_keywords = ['supply', 'consumable', 'inventory', 'stock', '消耗品', '庫存', '用品', '補給', '耗材']
            if any(keyword in user_message.lower() for keyword in consumable_keywords):
                consumables = self.ha_client.consumables.get_consumables()
                if consumables and not consumables.get('error'):
                    context['consumables'] = consumables
                    
        except Exception as e:
            self.logger.warning(f"Could not get backend context: {e}")
            
        return context

    def _enhance_prompt(self, user_message, context):
        """Enhance user prompt with backend context"""
        enhanced_prompt = user_message
        
        if context.get('schedules'):
            enhanced_prompt += f"\n\nCurrent schedules: {context['schedules']}"
            
        if context.get('consumables'):
            enhanced_prompt += f"\n\nCurrent consumables: {context['consumables']}"
            
        return enhanced_prompt

    def get_conversation_history(self, user_id: str):
        """獲取用戶的對話歷史"""
        history = self._get_user_conversation_history(user_id)
        return list(history)

    def clear_conversation_history(self, user_id: str):
        """清除用戶的對話歷史"""
        if user_id in self.conversation_histories:
            self.conversation_histories[user_id].clear()
            self.logger.info(f"Cleared conversation history for user {user_id}")

    def get_conversation_summary(self):
        """獲取所有用戶的對話歷史摘要"""
        summary = {}
        for user_id, history in self.conversation_histories.items():
            summary[user_id] = {
                "conversation_count": len(history),
                "last_conversation": history[-1]["timestamp"] if history else None
            }
        return summary
