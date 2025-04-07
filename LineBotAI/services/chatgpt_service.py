import requests
import logging

class ChatGPTService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

    def process_message(self, user_message):
        """Process user message using ChatGPT API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'text-davinci-003',
            'prompt': user_message,
            'max_tokens': 150
        }
        try:
            response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
            response.raise_for_status()
            return response.json().get('choices', [{}])[0].get('text', 'No response')
        except Exception as e:
            self.logger.error(f"ChatGPT API error: {e}")
            return "Error processing message."
