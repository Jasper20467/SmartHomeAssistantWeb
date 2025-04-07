import requests
import logging

class LineService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.logger = logging.getLogger(__name__)

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
        except Exception as e:
            self.logger.error(f"Error replying to LINE: {e}")
