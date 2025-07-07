#!/usr/bin/env python3
"""
Debug Environment Test Suite
調試環境測試套件

整合所有 debug 模式下的測試：
- 容器狀態檢查
- API 端點測試
- CRUD 操作測試
- LineBot 配置測試
- 服務間整合測試
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class DebugEnvironmentTester:
    """Debug 環境測試器"""
    
    def __init__(self):
        self.base_url = "http://localhost"
        self.api_base = f"{self.base_url}/api"
        self.test_results = {}
        
    def run_all_tests(self):
        """執行所有測試"""
        print("🏠 Smart Home Assistant Debug Environment Test Suite")
        print("=" * 60)
        print(f"🕐 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 目標環境: Debug (localhost)")
        print()
        
        tests = [
            ("容器狀態檢查", self.test_containers),
            ("基礎服務檢查", self.test_basic_services),
            ("API 端點測試", self.test_api_endpoints),
            ("CRUD 操作測試", self.test_crud_operations),
            ("LineBot 配置測試", self.test_linebot_config),
            ("服務整合測試", self.test_service_integration)
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}...")
            print("-" * 40)
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    print(f"✅ {test_name} - 通過")
                else:
                    print(f"❌ {test_name} - 失敗")
            except Exception as e:
                print(f"❌ {test_name} - 錯誤: {e}")
                self.test_results[test_name] = False
        
        self.print_summary()
    
    def test_containers(self):
        """檢查 Docker 容器狀態"""
        try:
            # 檢查 docker-compose 狀態
            result = subprocess.run(
                ["docker-compose", "ps", "--services", "--filter", "status=running"],
                capture_output=True, text=True, cwd=Path(__file__).parent.parent
            )
            
            if result.returncode == 0:
                running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
                expected_services = ['frontend', 'backend', 'linebot', 'db']
                
                print(f"   運行中的服務: {', '.join(running_services) if running_services else '無'}")
                
                all_running = all(service in running_services for service in expected_services)
                if all_running:
                    print("   ✅ 所有必要服務都在運行")
                else:
                    missing = [s for s in expected_services if s not in running_services]
                    print(f"   ⚠️  缺少服務: {', '.join(missing)}")
                
                return all_running
            else:
                print(f"   ❌ 無法檢查容器狀態: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ 容器檢查失敗: {e}")
            return False
    
    def test_basic_services(self):
        """測試基礎服務"""
        services = {
            "前端": f"{self.base_url}",
            "Backend API": f"{self.api_base}/schedules/",
            "LineBot Health": f"{self.base_url}/linebot/health"
        }
        
        all_ok = True
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ {service_name}: HTTP {response.status_code}")
                else:
                    print(f"   ❌ {service_name}: HTTP {response.status_code}")
                    all_ok = False
            except Exception as e:
                print(f"   ❌ {service_name}: {e}")
                all_ok = False
        
        return all_ok
    
    def test_api_endpoints(self):
        """測試 API 端點"""
        endpoints = [
            "/schedules/",
            "/consumables/"
        ]
        
        all_ok = True
        for endpoint in endpoints:
            try:
                url = f"{self.api_base}{endpoint}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {endpoint}: 返回 {len(data)} 項目")
                else:
                    print(f"   ❌ {endpoint}: HTTP {response.status_code}")
                    all_ok = False
            except Exception as e:
                print(f"   ❌ {endpoint}: {e}")
                all_ok = False
        
        return all_ok
    
    def test_crud_operations(self):
        """測試 CRUD 操作"""
        print("   🗓️  測試 Schedules CRUD...")
        schedules_ok = self._test_schedules_crud()
        
        print("   📦 測試 Consumables CRUD...")
        consumables_ok = self._test_consumables_crud()
        
        return schedules_ok and consumables_ok
    
    def _test_schedules_crud(self):
        """測試 schedules CRUD"""
        url = f"{self.api_base}/schedules/"
        
        # CREATE
        create_data = {
            "title": "Test Schedule Debug",
            "start_time": "2025-07-07T15:00:00",
            "description": "Debug environment test schedule"
        }
        
        try:
            # Create
            response = requests.post(url, json=create_data, timeout=10)
            if response.status_code not in [200, 201]:
                print(f"     ❌ CREATE 失敗: HTTP {response.status_code}")
                return False
            
            created_item = response.json()
            item_id = created_item.get('id')
            print(f"     ✅ CREATE: 創建 ID {item_id}")
            
            # READ
            response = requests.get(f"{url}{item_id}/", timeout=10)
            if response.status_code != 200:
                print(f"     ❌ READ 失敗: HTTP {response.status_code}")
                return False
            print("     ✅ READ: 成功讀取")
            
            # UPDATE
            update_data = create_data.copy()
            update_data["title"] = "Updated Test Schedule"
            response = requests.put(f"{url}{item_id}/", json=update_data, timeout=10)
            if response.status_code not in [200, 204]:
                print(f"     ❌ UPDATE 失敗: HTTP {response.status_code}")
                return False
            print("     ✅ UPDATE: 成功更新")
            
            # DELETE
            response = requests.delete(f"{url}{item_id}/", timeout=10)
            if response.status_code not in [200, 204]:
                print(f"     ❌ DELETE 失敗: HTTP {response.status_code}")
                return False
            print("     ✅ DELETE: 成功刪除")
            
            return True
            
        except Exception as e:
            print(f"     ❌ CRUD 測試失敗: {e}")
            return False
    
    def _test_consumables_crud(self):
        """測試 consumables CRUD"""
        url = f"{self.api_base}/consumables/"
        
        create_data = {
            "name": "Test Consumable Debug",
            "category": "test",
            "installation_date": "2025-07-07",
            "lifetime_days": 30,
            "notes": "Debug environment test consumable"
        }
        
        try:
            # Create
            response = requests.post(url, json=create_data, timeout=10)
            if response.status_code not in [200, 201]:
                print(f"     ❌ CREATE 失敗: HTTP {response.status_code}")
                return False
            
            created_item = response.json()
            item_id = created_item.get('id')
            print(f"     ✅ CREATE: 創建 ID {item_id}")
            
            # Delete (簡化測試)
            response = requests.delete(f"{url}{item_id}/", timeout=10)
            if response.status_code not in [200, 204]:
                print(f"     ❌ DELETE 失敗: HTTP {response.status_code}")
                return False
            print("     ✅ DELETE: 成功刪除")
            
            return True
            
        except Exception as e:
            print(f"     ❌ CRUD 測試失敗: {e}")
            return False
    
    def test_linebot_config(self):
        """測試 LineBot 配置"""
        try:
            # 檢查 LineBot 健康端點
            response = requests.get(f"{self.base_url}/linebot/health", timeout=10)
            if response.status_code != 200:
                print(f"   ❌ LineBot 健康檢查失敗: HTTP {response.status_code}")
                return False
            
            print("   ✅ LineBot 健康檢查通過")
            
            # 檢查 debug 端點
            try:
                response = requests.get(f"{self.base_url}/linebot/debug/config", timeout=10)
                if response.status_code == 200:
                    config = response.json()
                    print(f"   ✅ LineBot 配置: backend_url = {config.get('backend_url', 'N/A')}")
                    return True
                else:
                    print(f"   ⚠️ LineBot debug 配置不可用: HTTP {response.status_code}")
                    return True  # 非關鍵性失敗
            except Exception:
                # debug 端點可能不存在，這是正常的
                print("   ⚠️ LineBot debug 端點不可用（正常）")
                return True
                
        except Exception as e:
            print(f"   ❌ LineBot 測試失敗: {e}")
            return False
    
    def test_service_integration(self):
        """測試服務間整合"""
        try:
            # 測試前端到後端的連接
            response = requests.get(f"{self.base_url}/api/schedules/", timeout=10)
            if response.status_code != 200:
                print("   ❌ 前端到後端連接失敗")
                return False
            
            print("   ✅ 前端 ↔ 後端連接正常")
            
            # 測試 LineBot 到後端的連接
            try:
                response = requests.get(f"{self.base_url}/linebot/debug/test_backend", timeout=10)
                if response.status_code == 200:
                    print("   ✅ LineBot ↔ 後端連接正常")
                else:
                    print(f"   ⚠️ LineBot 到後端連接測試不可用")
            except Exception:
                print("   ⚠️ LineBot debug 端點不可用（正常）")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 整合測試失敗: {e}")
            return False
    
    def print_summary(self):
        """列印測試摘要"""
        print("\n" + "=" * 60)
        print("📊 測試結果摘要")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ 通過" if result else "❌ 失敗"
            print(f"  {status} {test_name}")
        
        print(f"\n📈 總計: {passed}/{total} 項測試通過")
        
        if passed == total:
            print("🎉 所有測試通過！Debug 環境運行正常。")
        else:
            print("⚠️  有測試失敗，請檢查 Debug 環境配置。")
        
        print(f"\n🕐 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函數"""
    tester = DebugEnvironmentTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
