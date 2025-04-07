from flask import Blueprint, request, jsonify
from debug_tests.test_handler import handle_debug_test

# 確保不直接匯入 `app.py`，避免循環匯入
debug_blueprint = Blueprint('debug', __name__)

@debug_blueprint.route('/api/debug/test', methods=['POST'])
def debug_test():
    """Debug testing endpoint for specific scenarios"""
    data = request.json
    return handle_debug_test(data)
