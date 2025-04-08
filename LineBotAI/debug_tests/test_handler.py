import logging
from flask import jsonify
from services.api_utils import call_chatgpt_api, call_backend_api, validate_request_format

logger = logging.getLogger(__name__)

def handle_debug_test(data):
    """Handle debug test scenarios."""
    test_mode = data.get('test_mode')
    user_message = data.get('message', '')

    if not test_mode or not user_message:
        return jsonify({"error": "Missing test_mode or message"}), 400

    handlers = {
        "1": handle_backend_only_test,
        "2": handle_chatgpt_and_backend_test
    }

    handler = handlers.get(test_mode)
    if handler:
        return handler(data)
    return jsonify({"error": "Invalid test_mode"}), 400

def handle_backend_only_test(data):
    """Handle test mode 1: Backend API interaction only."""
    if not validate_request_format(data):
        return jsonify({"error": "Invalid request format"}), 400

    # Example structure for user_message: {"category": "schedules", "operate": "GET", "content": {}}
    category = data.get("category")
    operate = data.get("operate")
    content = data.get("content", {})

    backend_response = call_backend_api(category, operate, content)
    return jsonify({"backend": backend_response})

def handle_chatgpt_and_backend_test(user_message):
    """Handle test mode 2: ChatGPT and Backend API interaction."""
    if not validate_request_format(user_message):
        return jsonify({"error": "Invalid request format"}), 400

    chatgpt_response = call_chatgpt_api(user_message)
    backend_response = call_backend_api(user_message.get("category"), user_message.get("operate"), user_message.get("content", {}))
    return jsonify({"chatgpt": chatgpt_response, "backend": backend_response})
