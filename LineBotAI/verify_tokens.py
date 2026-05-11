#!/usr/bin/env python3
"""
LineBot Token 驗證腳本
檢查目前打包的 LineBot 中的 Gemini 和 LINE API token 是否正確設定
"""

import os
import sys
import requests
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def check_environment_variables():
    """檢查環境變數設定"""
    print("=== 環境變數檢查 ===")
    
    # 檢查必要的環境變數
    required_vars = {
        'LINE_CHANNEL_ACCESS_TOKEN': os.getenv('LINE_CHANNEL_ACCESS_TOKEN', ''),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
        'GEMINI_MODEL': os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'),
        'BACKEND_API_URL': os.getenv('BACKEND_API_URL', ''),
        'DEBUG_MODE': os.getenv('DEBUG_MODE', 'false'),
        'DEBUG_STAGE': os.getenv('DEBUG_STAGE', 'false'),
        'DOMAIN_NAME': os.getenv('DOMAIN_NAME', 'localhost'),
        'TZ': os.getenv('TZ', 'UTC')
    }
    
    for var_name, var_value in required_vars.items():
        if var_value and var_value.strip():
            if var_name in ['LINE_CHANNEL_ACCESS_TOKEN', 'GEMINI_API_KEY']:
                # 只顯示前10個字符和後4個字符，中間用星號隱藏
                if len(var_value) > 14:
                    masked_value = var_value[:10] + '*' * (len(var_value) - 14) + var_value[-4:]
                else:
                    masked_value = var_value[:3] + '*' * (len(var_value) - 3)
                print(f"✓ {var_name}: {masked_value}")
            else:
                print(f"✓ {var_name}: {var_value}")
        else:
            print(f"✗ {var_name}: 未設定或為空")
    
    return required_vars

def test_line_api_token():
    """測試 LINE API Token 是否有效"""
    print("\n=== LINE API Token 測試 ===")
    
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
    
    if not line_token or line_token.strip() == '':
        print("✗ LINE Token 未設定")
        return False
    
    if line_token == 'your_line_channel_access_token':
        print("✗ LINE Token 使用的是預設值，請設定真實的 Token")
        return False
    
    # 測試 LINE API 連接
    try:
        headers = {
            'Authorization': f'Bearer {line_token}',
            'Content-Type': 'application/json'
        }
        
        # 使用 LINE Bot Info API 來驗證 Token
        response = requests.get('https://api.line.me/v2/bot/info', headers=headers, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✓ LINE Token 有效")
            print(f"  Bot Name: {bot_info.get('displayName', 'N/A')}")
            print(f"  Bot ID: {bot_info.get('userId', 'N/A')}")
            print(f"  Premium ID: {bot_info.get('premiumId', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("✗ LINE Token 無效或已過期")
            return False
        else:
            print(f"✗ LINE API 回應錯誤: {response.status_code}")
            print(f"  回應內容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ LINE API 連接失敗: {e}")
        return False

def test_gemini_api_key():
    """檢查 Gemini API Key 是否已設定"""
    print("\n=== Gemini API Key 檢查 ===")

    gemini_key = os.getenv('GEMINI_API_KEY', '')

    if not gemini_key or gemini_key.strip() == '':
        print("✗ GEMINI_API_KEY 未設定")
        return False

    if gemini_key == 'your_gemini_api_key_here':
        print("✗ GEMINI_API_KEY 使用的是預設佔位符，請設定真實的 API Key")
        return False

    gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    print(f"✓ GEMINI_API_KEY 已設定")
    print(f"  使用模型: {gemini_model}")
    return True

def test_backend_connectivity():
    """測試後端 API 連接性"""
    print("\n=== 後端 API 連接測試 ===")
    
    # 動態匯入以避免循環依賴
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config.url_config import get_backend_url
    
    backend_url = get_backend_url()
    print(f"後端 URL: {backend_url}")
    
    # 測試健康檢查端點
    try:
        if backend_url.startswith('http'):
            health_url = f"{backend_url}/health" if backend_url.endswith('/api') else f"{backend_url}/api/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                print("✓ 後端 API 連接成功")
                return True
            else:
                print(f"✗ 後端 API 回應錯誤: {response.status_code}")
                return False
        else:
            print("✗ 後端 URL 格式不正確")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 後端 API 連接失敗: {e}")
        return False

def main():
    """主要測試函數"""
    print("LineBot Token 驗證腳本")
    print("=" * 50)
    
    # 檢查環境變數
    env_vars = check_environment_variables()
    
    # 測試結果
    test_results = {
        'line_token': False,
        'gemini_key': False,
        'backend_connectivity': False
    }
    
    # 執行測試
    test_results['line_token'] = test_line_api_token()
    test_results['gemini_key'] = test_gemini_api_key()
    test_results['backend_connectivity'] = test_backend_connectivity()
    
    # 總結
    print("\n=== 測試總結 ===")
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{test_name}: {status}")
    
    print(f"\n總計: {passed_tests}/{total_tests} 測試通過")
    
    if passed_tests == total_tests:
        print("🎉 所有測試都通過！LineBot 應該可以正常運行。")
        return True
    else:
        print("⚠️  部分測試失敗，請檢查上述錯誤並修復。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
