#!/usr/bin/env python3
"""
CRUD 操作測試腳本

測試 debug mode 下所有 CRUD 操作是否正常
"""

import requests
import json
import time
from datetime import datetime, timedelta

class CRUDTester:
    def __init__(self, base_url="http://localhost"):
        self.base_url = base_url
        self.schedules_url = f"{base_url}/api/schedules/"
        self.consumables_url = f"{base_url}/api/consumables/"
        
    def test_schedules_crud(self):
        """測試 schedules 的 CRUD 操作"""
        print("🗓️  測試 Schedules CRUD 操作")
        print("-" * 40)
        
        # CREATE - 創建新的 schedule
        print("📝 測試 CREATE...")
        create_data = {
            "title": "Test Schedule",
            "start_time": "2025-07-07T15:00:00",
            "description": "This is a test schedule"
        }
        
        try:
            response = requests.post(self.schedules_url, json=create_data)
            if response.status_code == 201:
                created_schedule = response.json()
                schedule_id = created_schedule['id']
                print(f"   ✅ CREATE 成功: ID {schedule_id}")
            else:
                print(f"   ❌ CREATE 失敗: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ CREATE 錯誤: {e}")
            return False
        
        # READ - 讀取 schedule
        print("📖 測試 READ...")
        try:
            response = requests.get(f"{self.schedules_url}{schedule_id}")
            if response.status_code == 200:
                schedule = response.json()
                print(f"   ✅ READ 成功: {schedule['title']}")
            else:
                print(f"   ❌ READ 失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ READ 錯誤: {e}")
            return False
        
        # UPDATE - 更新 schedule
        print("✏️  測試 UPDATE...")
        update_data = {
            "title": "Updated Test Schedule",
            "start_time": "2025-07-07T16:00:00",
            "description": "This is an updated test schedule"
        }
        
        try:
            response = requests.put(f"{self.schedules_url}{schedule_id}", json=update_data)
            if response.status_code == 200:
                updated_schedule = response.json()
                print(f"   ✅ UPDATE 成功: {updated_schedule['title']}")
            else:
                print(f"   ❌ UPDATE 失敗: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ UPDATE 錯誤: {e}")
            return False
        
        # DELETE - 刪除 schedule
        print("🗑️  測試 DELETE...")
        try:
            response = requests.delete(f"{self.schedules_url}{schedule_id}")
            if response.status_code in [200, 204]:  # 接受 200 或 204 狀態碼
                print("   ✅ DELETE 成功")
            else:
                print(f"   ❌ DELETE 失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ DELETE 錯誤: {e}")
            return False
        
        return True
    
    def test_consumables_crud(self):
        """測試 consumables 的 CRUD 操作"""
        print("\n🧴 測試 Consumables CRUD 操作")
        print("-" * 40)
        
        # CREATE - 創建新的 consumable
        print("📝 測試 CREATE...")
        create_data = {
            "name": "Test Consumable",
            "category": "Test Category",
            "installation_date": "2025-07-07",
            "lifetime_days": 30,
            "notes": "This is a test consumable"
        }
        
        try:
            response = requests.post(self.consumables_url, json=create_data)
            if response.status_code == 201:
                created_consumable = response.json()
                consumable_id = created_consumable['id']
                print(f"   ✅ CREATE 成功: ID {consumable_id}")
            else:
                print(f"   ❌ CREATE 失敗: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ CREATE 錯誤: {e}")
            return False
        
        # READ - 讀取 consumable
        print("📖 測試 READ...")
        try:
            response = requests.get(f"{self.consumables_url}{consumable_id}")
            if response.status_code == 200:
                consumable = response.json()
                print(f"   ✅ READ 成功: {consumable['name']}")
            else:
                print(f"   ❌ READ 失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ READ 錯誤: {e}")
            return False
        
        # UPDATE - 更新 consumable
        print("✏️  測試 UPDATE...")
        update_data = {
            "name": "Updated Test Consumable",
            "category": "Updated Category",
            "installation_date": "2025-07-07",
            "lifetime_days": 60,
            "notes": "This is an updated test consumable"
        }
        
        try:
            response = requests.put(f"{self.consumables_url}{consumable_id}", json=update_data)
            if response.status_code == 200:
                updated_consumable = response.json()
                print(f"   ✅ UPDATE 成功: {updated_consumable['name']}")
            else:
                print(f"   ❌ UPDATE 失敗: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ UPDATE 錯誤: {e}")
            return False
        
        # DELETE - 刪除 consumable
        print("🗑️  測試 DELETE...")
        try:
            response = requests.delete(f"{self.consumables_url}{consumable_id}")
            if response.status_code in [200, 204]:  # 接受 200 或 204 狀態碼
                print("   ✅ DELETE 成功")
            else:
                print(f"   ❌ DELETE 失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ DELETE 錯誤: {e}")
            return False
        
        return True
    
    def test_list_operations(self):
        """測試列表操作"""
        print("\n📋 測試 LIST 操作")
        print("-" * 40)
        
        # 測試 schedules 列表
        print("📅 測試 Schedules 列表...")
        try:
            response = requests.get(self.schedules_url)
            if response.status_code == 200:
                schedules = response.json()
                print(f"   ✅ Schedules 列表成功: {len(schedules)} 筆記錄")
            else:
                print(f"   ❌ Schedules 列表失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Schedules 列表錯誤: {e}")
            return False
        
        # 測試 consumables 列表
        print("🧴 測試 Consumables 列表...")
        try:
            response = requests.get(self.consumables_url)
            if response.status_code == 200:
                consumables = response.json()
                print(f"   ✅ Consumables 列表成功: {len(consumables)} 筆記錄")
            else:
                print(f"   ❌ Consumables 列表失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Consumables 列表錯誤: {e}")
            return False
        
        return True
    
    def run_all_tests(self):
        """運行所有測試"""
        print("🧪 開始 CRUD 操作測試")
        print("=" * 60)
        
        results = []
        
        # 測試列表操作
        results.append(self.test_list_operations())
        
        # 測試 schedules CRUD
        results.append(self.test_schedules_crud())
        
        # 測試 consumables CRUD
        results.append(self.test_consumables_crud())
        
        # 結果摘要
        print("\n" + "=" * 60)
        print("📊 測試結果摘要")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ 通過: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 所有 CRUD 操作正常！")
            return True
        else:
            print("❌ 部分 CRUD 操作有問題，請檢查")
            return False

def main():
    """主程式"""
    print("🏠 Smart Home Assistant CRUD 測試")
    print("=" * 60)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("模式: Debug Mode (http://localhost)")
    
    tester = CRUDTester()
    
    if tester.run_all_tests():
        print("\n✅ 所有測試通過 - CRUD 操作正常")
        exit(0)
    else:
        print("\n❌ 測試失敗 - 請檢查問題")
        exit(1)

if __name__ == "__main__":
    main()
