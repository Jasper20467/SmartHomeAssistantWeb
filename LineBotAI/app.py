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
from config.url_config import get_backend_url

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY', '')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
DEBUG_STAGE = os.getenv('DEBUG_STAGE', 'false').lower() == 'true'

# Get backend URL using centralized configuration
BACKEND_API_URL = get_backend_url()
logger.info(f"Using backend URL: {BACKEND_API_URL}")
logger.info(f"Debug mode: {DEBUG_MODE}, Debug stage: {DEBUG_STAGE}")

def create_app():
    from routes.debug_routes import debug_blueprint  # 延遲匯入
    app = Flask(__name__)
    
    # Initialize services with backend URL
    line_service = LineService(LINE_CHANNEL_ACCESS_TOKEN, BACKEND_API_URL)
    chatgpt_service = ChatGPTService(CHATGPT_API_KEY, BACKEND_API_URL)
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Handle LINE webhook events"""
        try:
            body = request.json
            if body is None:
                return jsonify({'error': 'Invalid JSON or empty body'}), 400
            
            events = body.get('events', [])
            for event in events:
                reply_token = event.get('replyToken')
                user_message = event.get('message', {}).get('text', '')
                # 從 LINE 事件中提取 user_id
                user_id = event.get('source', {}).get('userId')
                
                if reply_token and user_message:
                    # Use the new sequence diagram flow with user_id for conversation history
                    line_service.process_user_message(user_message, reply_token, chatgpt_service, user_id)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return jsonify({'error': str(e)}), 400
    
    # Register blueprints
    app.register_blueprint(debug_blueprint)
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "ok"})
    
    @app.route('/linebot/health')
    def linebot_health():
        """LineBot specific health check endpoint"""
        return jsonify({
            "status": "ok",
            "service": "linebot",
            "backend_url": BACKEND_API_URL,
            "debug_mode": DEBUG_MODE,
            "debug_stage": DEBUG_STAGE
        })
    
    return app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'  # Make the app accessible externally in Docker
    
    logger.info(f"Starting LineBotAI with DEBUG_MODE={DEBUG_MODE}")
    app = create_app()

    app.run(host=host, port=port, debug=DEBUG_MODE)