import sys
import os

# Add the LineBotAI directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template_string
import requests
import json
import logging
from dotenv import load_dotenv
from services.line_service import LineService
from services.chatgpt_service import ChatGPTService

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY', '')
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
DEBUG_STAGE = os.getenv('DEBUG_STAGE', 'false').lower() == 'true'

def create_app():
    from routes.debug_routes import debug_blueprint  # 延遲匯入
    app = Flask(__name__)
    
    # Initialize services
    line_service = LineService(LINE_CHANNEL_ACCESS_TOKEN)
    chatgpt_service = ChatGPTService(CHATGPT_API_KEY)
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Handle LINE webhook events"""
        body = request.json
        events = body.get('events', [])
        for event in events:
            reply_token = event.get('replyToken')
            user_message = event.get('message', {}).get('text', '')
            if reply_token and user_message:
                response = chatgpt_service.process_message(user_message)
                line_service.reply_to_line(reply_token, response)
        return jsonify({'status': 'success'})
    
    # Register blueprints
    app.register_blueprint(debug_blueprint)
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "ok"})
    
    return app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'  # Make the app accessible externally in Docker
    
    logger.info(f"Starting LineBotAI with DEBUG_MODE={DEBUG_MODE}")
    app = create_app()
    app.run(host=host, port=port, debug=DEBUG_MODE)