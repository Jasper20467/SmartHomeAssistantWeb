from flask import Blueprint, request, jsonify
from debug_tests.test_handler import handle_debug_test
from config.url_config import get_backend_url
import os
import logging

# 確保不直接匯入 `app.py`，避免循環匯入
debug_blueprint = Blueprint('debug', __name__)
logger = logging.getLogger(__name__)

@debug_blueprint.route('/api/debug/test', methods=['POST'])
def debug_test():
    """Debug testing endpoint for specific scenarios"""
    data = request.json
    return handle_debug_test(data)

@debug_blueprint.route('/api/debug/backend', methods=['GET'])
def debug_backend():
    """Debug endpoint to test backend API connectivity"""
    try:
        from Home_assistant.client import HomeAssistantClient
        
        # Get backend URL using centralized configuration
        backend_url = get_backend_url()
        
        # Initialize client
        ha_client = HomeAssistantClient(backend_url)
        
        # Test connectivity
        result = {
            'backend_url': backend_url,
            'debug_mode': os.getenv('DEBUG_MODE', 'false'),
            'debug_stage': os.getenv('DEBUG_STAGE', 'false'),
            'domain_name': os.getenv('DOMAIN_NAME', 'localhost'),
            'tests': {}
        }
        
        # Test schedules endpoint
        try:
            schedules = ha_client.schedules.get_schedules()
            # Check if it's an error dict or a successful list
            if isinstance(schedules, dict) and schedules.get('error'):
                result['tests']['schedules'] = {
                    'status': 'error',
                    'error': schedules['error']
                }
            else:
                result['tests']['schedules'] = {
                    'status': 'success',
                    'data': schedules,
                    'count': len(schedules) if isinstance(schedules, list) else 0
                }
        except Exception as e:
            result['tests']['schedules'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Test consumables endpoint
        try:
            consumables = ha_client.consumables.get_consumables()
            # Check if it's an error dict or a successful list
            if isinstance(consumables, dict) and consumables.get('error'):
                result['tests']['consumables'] = {
                    'status': 'error',
                    'error': consumables['error']
                }
            else:
                result['tests']['consumables'] = {
                    'status': 'success',
                    'data': consumables,
                    'count': len(consumables) if isinstance(consumables, list) else 0
                }
        except Exception as e:
            result['tests']['consumables'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Debug backend test error: {e}")
        return jsonify({
            'error': str(e),
            'backend_url': get_backend_url()
        }), 500

@debug_blueprint.route('/api/debug/config', methods=['GET'])
def debug_config():
    """Debug endpoint to show current configuration"""
    return jsonify({
        'backend_url': get_backend_url(),
        'debug_mode': os.getenv('DEBUG_MODE', 'false'),
        'debug_stage': os.getenv('DEBUG_STAGE', 'false'),
        'domain_name': os.getenv('DOMAIN_NAME', 'localhost'),
        'line_token_set': bool(os.getenv('LINE_CHANNEL_ACCESS_TOKEN')),
        'chatgpt_key_set': bool(os.getenv('CHATGPT_API_KEY')),
        'timezone': os.getenv('TZ', 'UTC')
    })
