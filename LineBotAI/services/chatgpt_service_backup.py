import requests
import logging
import os
import json
from Home_assistant.client import HomeAssistantClient

class ChatGPTService:
    def __init__(self, api_key, backend_url=None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        # Initialize Home Assistant client for backend API calls
        self.backend_url = backend_url or os.getenv('BACKEND_API_URL', 'http://backend:8000')
        self.ha_client = HomeAssistantClient(self.backend_url)
        
        self.logger.info(f"ChatGPT service initialized with backend URL: {self.backend_url}")

    def process_message(self, user_message):
        """Process user message using ChatGPT API with backend integration"""
        try:
            # First, try to get context from backend API
            context = self._get_backend_context(user_message)
            
            # Enhance the prompt with backend context
            enhanced_prompt = self._enhance_prompt(user_message, context)
            
            # Call ChatGPT API
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'gpt-4.1-nano',
                'messages': [
                    {
                        'role': 'system',
                        'content': (
                            "You are a smart home assistant integrated with a LINE Bot.\n"
                            "\n"
                            "Your role:\n"
                            "- Understand user messages in Chinese.\n"
                            "- If the message requires performing backend operations related to schedules or consumables, return a JSON object with the specific action and parameters.\n"
                            "- If the user is only chatting or asking general questions, return a JSON object with action:\"text_reply\" and provide the reply text.\n"
                            "- If the user request does not contain all required information (e.g., missing schedule ID), do not guess. Instead, return an action that helps retrieve or clarify the needed information and include a reply asking the user.\n"
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
                            "1) User says: \"幫我建立一個排程，明天早上六點晨跑30分鐘\"\n"
                            "Return:\n"
                            "{\n"
                            "  \"action\": \"create_schedule\",\n"
                            "  \"parameters\": {\n"
                            "    \"title\": \"晨跑\",\n"
                            "    \"description\": \"每日晨跑\",\n"
                            "    \"start_time\": \"2025-07-09T06:00:00Z\",\n"
                            "    \"end_time\": \"2025-07-09T06:30:00Z\"\n"
                            "  },\n"
                            "  \"reply\": \"已為您建立排程：晨跑，明天早上6點開始。\"\n"
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
                            "\n"
                            "Important:\n"
                            "- Always respond with a valid JSON object.\n"
                            "- Dates must be in ISO 8601 format if needed.\n"
                            "- If any required information is missing, ask the user to provide it in the reply.\n"
                            "- Never guess IDs or date ranges."
                        )
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
                            "Important:\n"
                            "- Always respond with a valid JSON object.\n"
                            "- Dates must be in ISO 8601 format if needed.\n"
                            "- If any required information is missing, ask the user to provide it in the reply.\n"
                            "- Never guess IDs."
                        )
                    },
                    {
                        'role': 'user',
                        'content': enhanced_prompt
                    }
                ],
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
                    return json_response
                except json.JSONDecodeError:
                    # If not valid JSON, return as text reply
                    return {
                        "action": "text_reply",
                        "reply": content
                    }
            else:
                return {
                    "action": "text_reply",
                    "reply": "Sorry, I couldn't generate a response."
                }
                
        except Exception as e:
            self.logger.error(f"ChatGPT API error: {e}")
            return {
                "action": "text_reply",
                "reply": "Error processing message. Please try again."
            }

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
