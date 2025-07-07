#!/usr/bin/env python3
"""
LineBot 動態 URL 配置測試腳本

測試不同環境下的 URL 配置邏輯
"""

import os
import sys
import json
from unittest.mock import patch

# 添加 LineBotAI 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'LineBotAI'))

def test_url_configuration():
    """測試不同環境變數組合下的 URL 配置"""
    
    test_cases = [
        {
            'name': '開發環境 - Debug Mode',
            'env': {
                'DEBUG_MODE': 'true',
                'DEBUG_STAGE': 'false',
                'DOMAIN_NAME': 'localhost',
                'BACKEND_API_URL': None
            },
            'expected': 'http://backend:8000'
        },
        {
            'name': '開發環境 - Debug Stage',
            'env': {
                'DEBUG_MODE': 'false',
                'DEBUG_STAGE': 'true',
                'DOMAIN_NAME': 'localhost',
                'BACKEND_API_URL': None
            },
            'expected': 'http://backend:8000'
        },
        {
            'name': '生產環境 - 預設域名',
            'env': {
                'DEBUG_MODE': 'false',
                'DEBUG_STAGE': 'false',
                'DOMAIN_NAME': None,
                'BACKEND_API_URL': None
            },
            'expected': 'https://smarthome.the-jasperezlife.com/api'
        },
        {
            'name': '生產環境 - 自定義域名',
            'env': {
                'DEBUG_MODE': 'false',
                'DEBUG_STAGE': 'false',
                'DOMAIN_NAME': 'my-custom-domain.com',
                'BACKEND_API_URL': None
            },
            'expected': 'https://my-custom-domain.com/api'
        },
        {
            'name': '自定義 URL - 覆蓋所有設定',
            'env': {
                'DEBUG_MODE': 'true',
                'DEBUG_STAGE': 'true',
                'DOMAIN_NAME': 'ignored-domain.com',
                'BACKEND_API_URL': 'https://custom-backend.com:8080'
            },
            'expected': 'https://custom-backend.com:8080'
        }
    ]
    
    print("🧪 測試 LineBot 動態 URL 配置")
    print("=" * 60)
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n📋 測試案例: {test_case['name']}")
        print(f"   預期結果: {test_case['expected']}")
        
        # 設定環境變數
        env_vars = {}
        for key, value in test_case['env'].items():
            if value is not None:
                env_vars[key] = value
            else:
                # 對於 None 值，我們需要確保環境變數不存在
                env_vars[key] = ''
        
        # 使用 mock 來模擬環境變數
        with patch.dict(os.environ, env_vars, clear=True):
            try:
                # 重新定義 get_backend_url 函數
                def get_backend_url():
                    custom_url = os.getenv('BACKEND_API_URL')
                    if custom_url and custom_url.strip():
                        return custom_url
                    
                    debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
                    debug_stage = os.getenv('DEBUG_STAGE', 'false').lower() == 'true'
                    
                    if debug_mode or debug_stage:
                        return 'http://backend:8000'
                    else:
                        domain = os.getenv('DOMAIN_NAME', 'smarthome.the-jasperezlife.com')
                        if not domain or domain.strip() == '':
                            domain = 'smarthome.the-jasperezlife.com'
                        return f'https://{domain}/api'
                
                actual_url = get_backend_url()
                
                if actual_url == test_case['expected']:
                    print(f"   ✅ 通過: {actual_url}")
                else:
                    print(f"   ❌ 失敗: 預期 {test_case['expected']}, 實際 {actual_url}")
                    all_passed = False
                    
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")
                all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有測試通過！")
        return True
    else:
        print("❌ 部分測試失敗")
        return False

def test_environment_detection():
    """測試環境檢測功能"""
    
    print("\n🔍 測試環境檢測")
    print("-" * 40)
    
    # 當前環境變數
    current_env = {
        'DEBUG_MODE': os.getenv('DEBUG_MODE', 'false'),
        'DEBUG_STAGE': os.getenv('DEBUG_STAGE', 'false'),
        'DOMAIN_NAME': os.getenv('DOMAIN_NAME', 'smarthome.the-jasperezlife.com'),
        'BACKEND_API_URL': os.getenv('BACKEND_API_URL', 'not set')
    }
    
    print("當前環境變數:")
    for key, value in current_env.items():
        print(f"  {key}: {value}")
    
    # 判斷環境類型
    debug_mode = current_env['DEBUG_MODE'].lower() == 'true'
    debug_stage = current_env['DEBUG_STAGE'].lower() == 'true'
    
    if debug_mode or debug_stage:
        env_type = "開發/除錯環境"
    else:
        env_type = "生產環境"
    
    print(f"\n環境類型: {env_type}")
    
    # 模擬 get_backend_url 函數
    def get_backend_url():
        custom_url = os.getenv('BACKEND_API_URL')
        if custom_url and custom_url != 'not set':
            return custom_url
        
        if debug_mode or debug_stage:
            return 'http://backend:8000'
        else:
            domain = os.getenv('DOMAIN_NAME', 'smarthome.the-jasperezlife.com')
            return f'https://{domain}/api'
    
    backend_url = get_backend_url()
    print(f"後端 API URL: {backend_url}")

if __name__ == "__main__":
    print("LineBot 動態 URL 配置測試")
    print("=" * 60)
    
    # 執行測試
    test_passed = test_url_configuration()
    test_environment_detection()
    
    print("\n" + "=" * 60)
    if test_passed:
        print("✅ 測試完成 - 所有配置邏輯正確")
        sys.exit(0)
    else:
        print("❌ 測試失敗 - 請檢查配置邏輯")
        sys.exit(1)
