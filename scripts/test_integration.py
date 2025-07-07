#!/usr/bin/env python3
"""
Smart Home Assistant 整合測試腳本

測試所有服務間的交握：frontend ↔ backend ↔ linebot ↔ db
在 debug mode 和 production mode 下進行測試
"""

import os
import sys
import json
import time
import requests
import asyncio
import subprocess
from typing import Dict, List, Any
from urllib.parse import urljoin

class ServiceTester:
    """服務測試類別"""
    
    def __init__(self, mode: str = "debug"):
        self.mode = mode
        self.base_urls = self._get_base_urls()
        self.test_results = {}
        
    def _get_base_urls(self) -> Dict[str, str]:
        """根據模式獲取服務的基本 URL"""
        if self.mode == "debug":
            return {
                'frontend': 'http://localhost:80',
                'backend': 'http://localhost:8000',
                'linebot': 'http://localhost:5000',
                'db': 'postgresql://postgres:postgres@localhost:5432/smarthome'
            }
        else:  # production
            domain = "smarthome.the-jasperezlife.com"
            return {
                'frontend': f'https://{domain}',
                'backend': f'https://{domain}/api',
                'linebot': f'https://{domain}',
                'db': 'postgresql://postgres:postgres@db:5432/smarthome'
            }
    
    def test_service_health(self) -> Dict[str, Any]:
        """測試各服務的健康狀態"""
        print(f"\n🏥 測試服務健康狀態 ({self.mode} mode)")
        print("-" * 50)
        
        health_results = {}
        
        # Test Backend Health
        print("🔧 測試 Backend...")
        try:
            response = requests.get(f"{self.base_urls['backend']}/health", timeout=10)
            if response.status_code == 200:
                health_results['backend'] = {'status': 'healthy', 'response': response.json()}
                print("   ✅ Backend: 正常")
            else:
                health_results['backend'] = {'status': 'unhealthy', 'error': f"HTTP {response.status_code}"}
                print(f"   ❌ Backend: HTTP {response.status_code}")
        except Exception as e:
            health_results['backend'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Backend: {e}")
        
        # Test LineBot Health
        print("🤖 測試 LineBot...")
        try:
            response = requests.get(f"{self.base_urls['linebot']}/linebot/health", timeout=10)
            if response.status_code == 200:
                health_results['linebot'] = {'status': 'healthy', 'response': response.json()}
                print("   ✅ LineBot: 正常")
            else:
                health_results['linebot'] = {'status': 'unhealthy', 'error': f"HTTP {response.status_code}"}
                print(f"   ❌ LineBot: HTTP {response.status_code}")
        except Exception as e:
            # 嘗試使用 /api/health 端點
            try:
                response = requests.get(f"{self.base_urls['linebot']}/api/health", timeout=10)
                if response.status_code == 200:
                    health_results['linebot'] = {'status': 'healthy', 'response': response.json()}
                    print("   ✅ LineBot: 正常")
                else:
                    health_results['linebot'] = {'status': 'unhealthy', 'error': f"HTTP {response.status_code}"}
                    print(f"   ❌ LineBot: HTTP {response.status_code}")
            except Exception as e2:
                health_results['linebot'] = {'status': 'error', 'error': str(e2)}
                print(f"   ❌ LineBot: {e2}")
        
        # Test Frontend (簡單檢查是否回應)
        print("🌐 測試 Frontend...")
        try:
            response = requests.get(self.base_urls['frontend'], timeout=10)
            if response.status_code == 200:
                health_results['frontend'] = {'status': 'healthy', 'response': 'HTML content received'}
                print("   ✅ Frontend: 正常")
            else:
                health_results['frontend'] = {'status': 'unhealthy', 'error': f"HTTP {response.status_code}"}
                print(f"   ❌ Frontend: HTTP {response.status_code}")
        except Exception as e:
            health_results['frontend'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Frontend: {e}")
        
        return health_results
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """測試 API 端點"""
        print(f"\n🔌 測試 API 端點 ({self.mode} mode)")
        print("-" * 50)
        
        api_results = {}
        
        # Test Backend API directly
        print("🔧 測試 Backend API...")
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/api/schedules", "GET"),
            ("/api/consumables", "GET"),
        ]
        
        for endpoint, method in endpoints:
            try:
                url = f"{self.base_urls['backend']}{endpoint}"
                response = requests.request(method, url, timeout=10)
                if response.status_code in [200, 404]:  # 404 可能表示端點存在但無資料
                    api_results[f"backend{endpoint}"] = {'status': 'success', 'code': response.status_code}
                    print(f"   ✅ {method} {endpoint}: HTTP {response.status_code}")
                else:
                    api_results[f"backend{endpoint}"] = {'status': 'error', 'code': response.status_code}
                    print(f"   ❌ {method} {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                api_results[f"backend{endpoint}"] = {'status': 'error', 'error': str(e)}
                print(f"   ❌ {method} {endpoint}: {e}")
        
        return api_results
    
    def test_frontend_backend_integration(self) -> Dict[str, Any]:
        """測試 Frontend 與 Backend 的整合"""
        print(f"\n🔄 測試 Frontend ↔ Backend 整合 ({self.mode} mode)")
        print("-" * 50)
        
        integration_results = {}
        
        # 在 debug mode 下，測試 Frontend 是否能透過 nginx proxy 訪問 backend
        if self.mode == "debug":
            frontend_api_base = f"{self.base_urls['frontend']}/api"
        else:
            frontend_api_base = f"{self.base_urls['backend']}"
        
        print("🌐 測試 Frontend → Backend 代理...")
        endpoints = [
            "/schedules",
            "/consumables",
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{frontend_api_base}{endpoint}"
                response = requests.get(url, timeout=10)
                if response.status_code in [200, 404]:
                    integration_results[f"frontend_proxy{endpoint}"] = {'status': 'success', 'code': response.status_code}
                    print(f"   ✅ Frontend → Backend {endpoint}: HTTP {response.status_code}")
                else:
                    integration_results[f"frontend_proxy{endpoint}"] = {'status': 'error', 'code': response.status_code}
                    print(f"   ❌ Frontend → Backend {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                integration_results[f"frontend_proxy{endpoint}"] = {'status': 'error', 'error': str(e)}
                print(f"   ❌ Frontend → Backend {endpoint}: {e}")
        
        return integration_results
    
    def test_linebot_backend_integration(self) -> Dict[str, Any]:
        """測試 LineBot 與 Backend 的整合"""
        print(f"\n🤖 測試 LineBot ↔ Backend 整合 ({self.mode} mode)")
        print("-" * 50)
        
        linebot_results = {}
        
        # Test LineBot configuration endpoint
        print("🔧 測試 LineBot 配置...")
        try:
            if self.mode == "debug":
                config_url = f"{self.base_urls['linebot']}/api/debug/config"
            else:
                config_url = f"{self.base_urls['linebot']}/api/debug/config"
                
            response = requests.get(config_url, timeout=10)
            if response.status_code == 200:
                config_data = response.json()
                linebot_results['config'] = {'status': 'success', 'data': config_data}
                print(f"   ✅ LineBot 配置: {config_data.get('backend_url', 'N/A')}")
            else:
                linebot_results['config'] = {'status': 'error', 'code': response.status_code}
                print(f"   ❌ LineBot 配置: HTTP {response.status_code}")
        except Exception as e:
            linebot_results['config'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ LineBot 配置: {e}")
        
        # Test LineBot backend connectivity
        print("🔗 測試 LineBot → Backend 連接...")
        try:
            if self.mode == "debug":
                backend_test_url = f"{self.base_urls['linebot']}/api/debug/backend"
            else:
                backend_test_url = f"{self.base_urls['linebot']}/api/debug/backend"
                
            response = requests.get(backend_test_url, timeout=15)
            if response.status_code == 200:
                backend_data = response.json()
                linebot_results['backend_connectivity'] = {'status': 'success', 'data': backend_data}
                print("   ✅ LineBot → Backend: 連接正常")
                
                # 檢查測試結果
                tests = backend_data.get('tests', {})
                for test_name, test_result in tests.items():
                    status = test_result.get('status', 'unknown')
                    if status == 'success':
                        print(f"      ✅ {test_name}: 成功")
                    else:
                        print(f"      ❌ {test_name}: {test_result.get('error', 'failed')}")
                        
            else:
                linebot_results['backend_connectivity'] = {'status': 'error', 'code': response.status_code}
                print(f"   ❌ LineBot → Backend: HTTP {response.status_code}")
        except Exception as e:
            linebot_results['backend_connectivity'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ LineBot → Backend: {e}")
        
        return linebot_results
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """測試資料庫連接"""
        print(f"\n💾 測試資料庫連接 ({self.mode} mode)")
        print("-" * 50)
        
        db_results = {}
        
        # 透過 Backend API 測試資料庫連接
        print("🔧 測試 Backend → Database...")
        try:
            # 嘗試訪問需要資料庫的端點
            response = requests.get(f"{self.base_urls['backend']}/api/schedules", timeout=10)
            if response.status_code in [200, 404]:  # 404 也表示端點存在，只是沒有資料
                db_results['backend_db'] = {'status': 'success', 'code': response.status_code}
                print(f"   ✅ Backend → Database: HTTP {response.status_code} (連接正常)")
            else:
                db_results['backend_db'] = {'status': 'error', 'code': response.status_code}
                print(f"   ❌ Backend → Database: HTTP {response.status_code}")
        except Exception as e:
            db_results['backend_db'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Backend → Database: {e}")
        
        return db_results
    
    def run_full_test(self) -> Dict[str, Any]:
        """執行完整測試"""
        print(f"🧪 開始整合測試 - {self.mode.upper()} MODE")
        print("=" * 60)
        
        all_results = {
            'mode': self.mode,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_urls': self.base_urls,
            'tests': {}
        }
        
        # 執行各項測試
        all_results['tests']['health'] = self.test_service_health()
        all_results['tests']['api'] = self.test_api_endpoints()
        all_results['tests']['frontend_backend'] = self.test_frontend_backend_integration()
        all_results['tests']['linebot_backend'] = self.test_linebot_backend_integration()
        all_results['tests']['database'] = self.test_database_connectivity()
        
        return all_results

def print_summary(results: Dict[str, Any]):
    """打印測試結果摘要"""
    print("\n" + "=" * 60)
    print(f"📊 測試結果摘要 - {results['mode'].upper()} MODE")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, tests in results['tests'].items():
        print(f"\n📋 {category.upper()}")
        for test_name, test_result in tests.items():
            total_tests += 1
            status = test_result.get('status', 'unknown')
            if status in ['success', 'healthy']:
                passed_tests += 1
                print(f"   ✅ {test_name}")
            else:
                print(f"   ❌ {test_name}: {test_result.get('error', test_result.get('code', 'unknown'))}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📈 成功率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 整體狀態: 良好")
        return True
    elif success_rate >= 60:
        print("⚠️  整體狀態: 需要注意")
        return False
    else:
        print("❌ 整體狀態: 需要修復")
        return False

def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Home Assistant 整合測試')
    parser.add_argument('--mode', choices=['debug', 'production'], default='debug',
                       help='測試模式 (預設: debug)')
    parser.add_argument('--output', help='輸出結果到 JSON 檔案')
    
    args = parser.parse_args()
    
    print("🏠 Smart Home Assistant 整合測試")
    print("=" * 60)
    print(f"模式: {args.mode}")
    print(f"時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 執行測試
    tester = ServiceTester(args.mode)
    results = tester.run_full_test()
    
    # 打印摘要
    success = print_summary(results)
    
    # 輸出結果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 詳細結果已保存到: {args.output}")
    
    # 結束
    print("\n" + "=" * 60)
    if success:
        print("✅ 測試完成 - 系統狀態良好")
        sys.exit(0)
    else:
        print("❌ 測試完成 - 發現問題，請檢查")
        sys.exit(1)

if __name__ == "__main__":
    main()
