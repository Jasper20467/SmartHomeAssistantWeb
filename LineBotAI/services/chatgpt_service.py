import requests
import logging
import os
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
                'model': 'gpt-3.5-turbo',  # Updated to newer model
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a smart home assistant. Help users manage their home automation, schedules, and consumables.'
                    },
                    {
                        'role': 'user',
                        'content': enhanced_prompt
                    }
                ],
                'max_tokens': 150
            }
            
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "Sorry, I couldn't generate a response."
                
        except Exception as e:
            self.logger.error(f"ChatGPT API error: {e}")
            return "Error processing message. Please try again."

    def _get_backend_context(self, user_message):
        """Get relevant context from backend API"""
        context = {}
        
        try:
            # Try to get schedules if message relates to scheduling
            if any(keyword in user_message.lower() for keyword in ['schedule', 'appointment', 'reminder', 'time']):
                schedules = self.ha_client.schedules.get_schedules()
                if schedules and not schedules.get('error'):
                    context['schedules'] = schedules
            
            # Try to get consumables if message relates to supplies
            if any(keyword in user_message.lower() for keyword in ['supply', 'consumable', 'inventory', 'stock']):
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
