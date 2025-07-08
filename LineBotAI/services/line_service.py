import requests
import logging
import json
from Home_assistant.client import HomeAssistantClient

class LineService:
    def __init__(self, access_token, backend_url=None):
        self.access_token = access_token
        self.logger = logging.getLogger(__name__)
        
        # Initialize Home Assistant client for backend API calls
        self.backend_url = backend_url
        if backend_url:
            self.ha_client = HomeAssistantClient(backend_url)
        else:
            self.ha_client = None
            
        self.logger.info(f"LineBot service initialized with backend URL: {self.backend_url}")

    def process_user_message(self, user_message, reply_token, chatgpt_service, user_id=None):
        """Process user message according to the sequence diagram flow"""
        try:
            # Step 1: Call ChatGPT API to get JSON response with user_id for conversation history
            chatgpt_response = chatgpt_service.process_message(user_message, user_id)
            
            if not isinstance(chatgpt_response, dict):
                # Fallback if not JSON
                self.reply_to_line(reply_token, str(chatgpt_response))
                return
            
            action = chatgpt_response.get('action')
            parameters = chatgpt_response.get('parameters', {})
            reply_text = chatgpt_response.get('reply', '')
            
            # Step 2: Check if action requires backend operation
            if action == 'text_reply':
                # Direct text reply
                self.reply_to_line(reply_token, reply_text)
            else:
                # Backend operation required
                backend_result = self._perform_backend_operation(action, parameters)
                final_reply = self._format_backend_response(reply_text, backend_result, action, parameters)
                self.reply_to_line(reply_token, final_reply)
                
        except Exception as e:
            self.logger.error(f"Error processing user message: {e}")
            self.reply_to_line(reply_token, "抱歉，處理您的請求時發生錯誤。請稍後再試。")

    def _perform_backend_operation(self, action, parameters):
        """Perform backend API operation based on action"""
        if not self.ha_client:
            return {"error": "Backend client not initialized"}
            
        try:
            if action == 'create_schedule':
                return self.ha_client.schedules.create_schedule(parameters)
            elif action == 'get_schedule':
                # Check if we have date parameter for filtering
                date_param = parameters.get('date')
                if date_param:
                    return self.ha_client.schedules.get_schedules(date=date_param)
                else:
                    return self.ha_client.schedules.get_schedules()
            elif action == 'update_schedule':
                schedule_id = parameters.get('id')
                if schedule_id:
                    return self.ha_client.schedules.update_schedule(schedule_id, parameters)
                else:
                    return {"error": "Schedule ID required for update"}
            elif action == 'delete_schedule':
                schedule_id = parameters.get('id')
                if schedule_id:
                    return self.ha_client.schedules.delete_schedule(schedule_id)
                else:
                    return {"error": "Schedule ID required for deletion"}
            elif action == 'create_consumable':
                return self.ha_client.consumables.create_consumable(parameters)
            elif action == 'get_consumable':
                return self.ha_client.consumables.get_consumables()
            elif action == 'update_consumable':
                consumable_id = parameters.get('id')
                if consumable_id:
                    return self.ha_client.consumables.update_consumable(consumable_id, parameters)
                else:
                    return {"error": "Consumable ID required for update"}
            elif action == 'delete_consumable':
                consumable_id = parameters.get('id')
                if consumable_id:
                    return self.ha_client.consumables.delete_consumable(consumable_id)
                else:
                    return {"error": "Consumable ID required for deletion"}
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Backend operation error: {e}")
            return {"error": str(e)}

    def _format_backend_response(self, original_reply, backend_result, action, parameters=None):
        """Format the final response based on backend result"""
        # Handle if backend_result is a list
        if isinstance(backend_result, list):
            # For get_schedule or get_consumable, treat the list as the result
            if action == 'get_schedule':
                schedules = backend_result
                if schedules:
                    date_param = parameters.get('date') if parameters else None
                    if date_param:
                        schedule_list = "\n".join([f"• ID {s.get('id', 'N/A')}: {s.get('title', 'Unknown')} ({s.get('start_time', 'N/A')})" for s in schedules])
                        return f"{original_reply}\n\n📅 {date_param} 的排程:\n{schedule_list}"
                    else:
                        schedule_list = "\n".join([f"• {s.get('title', 'Unknown')}: {s.get('start_time', 'N/A')}" for s in schedules])
                        return f"{original_reply}\n\n📅 目前排程:\n{schedule_list}"
                else:
                    return f"{original_reply}\n\n📅 目前沒有排程。"
            elif action == 'get_consumable':
                consumables = backend_result
                if consumables:
                    consumable_list = "\n".join([f"• {c.get('name', 'Unknown')}: {c.get('quantity', 'N/A')}" for c in consumables])
                    return f"{original_reply}\n\n📦 目前消耗品:\n{consumable_list}"
                else:
                    return f"{original_reply}\n\n📦 目前沒有消耗品。"
            else:
                return original_reply

        # Handle if backend_result is a dict
        if isinstance(backend_result, dict) and backend_result.get('error'):
            return f"{original_reply}\n\n❌ 操作失敗: {backend_result['error']}"
        
        # Success cases
        if action in ['create_schedule', 'create_consumable']:
            return f"{original_reply}\n\n✅ 建立成功！"
        elif action in ['update_schedule', 'update_consumable']:
            return f"{original_reply}\n\n✅ 更新成功！"
        elif action in ['delete_schedule', 'delete_consumable']:
            return f"{original_reply}\n\n✅ 刪除成功！"
        elif action == 'get_schedule':
            schedules = backend_result.get('schedules', []) if isinstance(backend_result, dict) else []
            if schedules:
                date_param = parameters.get('date') if parameters else None
                if date_param:
                    schedule_list = "\n".join([f"• ID {s.get('id', 'N/A')}: {s.get('title', 'Unknown')} ({s.get('start_time', 'N/A')})" for s in schedules])
                    return f"{original_reply}\n\n📅 {date_param} 的排程:\n{schedule_list}"
                else:
                    schedule_list = "\n".join([f"• {s.get('title', 'Unknown')}: {s.get('start_time', 'N/A')}" for s in schedules])
                    return f"{original_reply}\n\n📅 目前排程:\n{schedule_list}"
            else:
                return f"{original_reply}\n\n📅 目前沒有排程。"
        elif action == 'get_consumable':
            consumables = backend_result.get('consumables', []) if isinstance(backend_result, dict) else []
            if consumables:
                consumable_list = "\n".join([f"• {c.get('name', 'Unknown')}: {c.get('quantity', 'N/A')}" for c in consumables])
                return f"{original_reply}\n\n📦 目前消耗品:\n{consumable_list}"
            else:
                return f"{original_reply}\n\n📦 目前沒有消耗品。"
        else:
            return original_reply

    def reply_to_line(self, reply_token, message):
        """Send response back to LINE"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        data = {
            'replyToken': reply_token,
            'messages': [{'type': 'text', 'text': message}]
        }
        try:
            response = requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=data)
            response.raise_for_status()
            self.logger.info(f"Successfully sent reply to LINE")
        except Exception as e:
            self.logger.error(f"Error replying to LINE: {e}")
