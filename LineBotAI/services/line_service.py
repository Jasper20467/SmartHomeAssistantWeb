import requests
import logging
from services.agent_service import AgentService


class LineService:
    def __init__(self, access_token, backend_url=None):
        self.access_token = access_token
        self.logger = logging.getLogger(__name__)

        self.backend_url = backend_url
        if backend_url:
            self.agent_service = AgentService(backend_url)
        else:
            self.agent_service = None

        self.logger.info(f"LineBot service initialized with backend URL: {self.backend_url}")

    def process_user_message(self, user_message, reply_token, user_id=None):
        """Process user message via LangGraph ReAct Agent."""
        try:
            if not self.agent_service:
                self.reply_to_line(reply_token, "抱歉，服務尚未初始化，請稍後再試。")
                return

            reply_text = self.agent_service.run(user_message, user_id or "anonymous")
            self.reply_to_line(reply_token, reply_text)
        except Exception as e:
            self.logger.error(f"Error processing user message: {e}")
            self.reply_to_line(reply_token, "抱歉，處理您的請求時發生錯誤。請稍後再試。")

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
