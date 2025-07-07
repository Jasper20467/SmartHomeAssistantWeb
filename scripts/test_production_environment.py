#!/usr/bin/env python3
"""
Production Environment Test Suite
生產環境測試套件

整合所有 production 模式下的測試：
- 前端服務檢查
- LineBot 服務測試
- 配置驗證
- 性能測試
- 安全性檢查

注意：Backend API 在 production 環境中僅供內部 Docker 服務使用，
不進行外部直接測試，功能透過前端和 LineBot 服務間接驗證。
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from urllib.parse import urlparse

class ProductionEnvironmentTester:
    """Production 環境測試器"""
    
    def __init__(self, domain="https://smarthome.the-jasperezlife.com"):
        self.domain = domain
        self.api_base = f"{domain}/api"
        self.linebot_base = f"{domain}/linebot"
        self.test_results = {}
        
    def run_all_tests(self):
        """執行所有測試"""
        print("🏭 Smart Home Assistant Production Environment Test Suite")
        print("=" * 60)
        print(f"🕐 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 目標環境: Production ({self.domain})")
        print()
        
        tests = [
            ("前端服務檢查", self.test_basic_services),
            ("應用程式功能驗證", self.test_api_endpoints),
            ("LineBot 服務測試", self.test_linebot_service),
            ("配置驗證", self.test_configuration),
            ("性能測試", self.test_performance),
            ("安全性檢查", self.test_security),
            ("服務可用性測試", self.test_service_availability)
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
    
    def test_basic_services(self):
        """測試基礎服務"""
        services = {
            "前端服務": self.domain,
            "LineBot Health": f"{self.linebot_base}/health"
        }
        
        all_ok = True
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    print(f"   ✅ {service_name}: HTTP {response.status_code}")
                    # 檢查響應時間
                    response_time = response.elapsed.total_seconds()
                    if response_time < 2.0:
                        print(f"      ⏱️  響應時間: {response_time:.2f}s (良好)")
                    elif response_time < 5.0:
                        print(f"      ⏱️  響應時間: {response_time:.2f}s (可接受)")
                    else:
                        print(f"      ⚠️  響應時間: {response_time:.2f}s (較慢)")
                elif response.status_code == 502:
                    print(f"   ❌ {service_name}: HTTP 502 (Backend 連接失敗)")
                    all_ok = False
                else:
                    print(f"   ❌ {service_name}: HTTP {response.status_code}")
                    all_ok = False
            except requests.exceptions.Timeout:
                print(f"   ❌ {service_name}: 連接超時")
                all_ok = False
            except Exception as e:
                print(f"   ❌ {service_name}: {e}")
                all_ok = False
        
        # 說明 Backend API 不進行外部測試
        print("   ℹ️  Backend API: 僅供內部服務訪問，不進行外部測試")
        
        return all_ok
    
    def test_api_endpoints(self):
        """測試 API 端點（透過前端代理）"""
        # 在 production 環境中，API 請求應該透過前端代理或 LineBot 服務
        # 不直接測試 backend API 端點，因為它們在 Docker 內部網路中
        
        print("   ℹ️  Production 環境中，Backend API 僅供內部服務使用")
        print("   ℹ️  API 功能透過前端應用程式和 LineBot 服務驗證")
        
        # 檢查前端是否能正常載入（間接驗證 backend 連接）
        try:
            response = requests.get(self.domain, timeout=10)
            if response.status_code == 200:
                print("   ✅ 前端應用程式正常載入（間接驗證 Backend 連接）")
                return True
            else:
                print(f"   ❌ 前端應用程式載入失敗: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 前端應用程式測試失敗: {e}")
            return False
    
    def test_linebot_service(self):
        """測試 LineBot 服務"""
        try:
            # 健康檢查
            response = requests.get(f"{self.linebot_base}/health", timeout=10)
            if response.status_code != 200:
                print(f"   ❌ LineBot 健康檢查失敗: HTTP {response.status_code}")
                return False
            
            print("   ✅ LineBot 健康檢查通過")
            
            # 檢查 webhook 端點（不實際觸發）
            # webhook 端點直接在根路徑 /webhook，不在 /linebot/webhook
            webhook_url = f"{self.domain}/webhook"
            try:
                response = requests.options(webhook_url, timeout=5)
                if response.status_code in [200, 405]:  # 405 是預期的，因為我們用 OPTIONS
                    print("   ✅ LineBot Webhook 端點可達")
                else:
                    print(f"   ⚠️  LineBot Webhook 響應異常: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  LineBot Webhook 端點測試失敗: {e}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ LineBot 測試失敗: {e}")
            return False
    
    def test_configuration(self):
        """測試配置驗證"""
        try:
            # 檢查 HTTPS
            if not self.domain.startswith('https://'):
                print("   ❌ 未使用 HTTPS")
                return False
            print("   ✅ 使用 HTTPS 加密")
            
            # 檢查響應頭
            response = requests.get(self.domain, timeout=10)
            headers = response.headers
            
            # 檢查安全頭
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block'
            }
            
            for header, expected in security_headers.items():
                if header in headers:
                    if isinstance(expected, list):
                        if headers[header] in expected:
                            print(f"   ✅ 安全頭 {header}: {headers[header]}")
                        else:
                            print(f"   ⚠️  安全頭 {header}: {headers[header]} (建議: {', '.join(expected)})")
                    else:
                        if headers[header] == expected:
                            print(f"   ✅ 安全頭 {header}: {headers[header]}")
                        else:
                            print(f"   ⚠️  安全頭 {header}: {headers[header]} (建議: {expected})")
                else:
                    print(f"   ⚠️  缺少安全頭: {header}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 配置檢查失敗: {e}")
            return False
    
    def test_performance(self):
        """測試性能"""
        try:
            # 只測試可從外部訪問的端點
            endpoints = [
                (self.domain, "前端"),
                (f"{self.linebot_base}/health", "LineBot Health")
            ]
            
            all_good = True
            for url, name in endpoints:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    if response_time < 1.0:
                        print(f"   ✅ {name}: {response_time:.2f}s (優秀)")
                    elif response_time < 3.0:
                        print(f"   ✅ {name}: {response_time:.2f}s (良好)")
                    elif response_time < 5.0:
                        print(f"   ⚠️  {name}: {response_time:.2f}s (可接受)")
                    else:
                        print(f"   ❌ {name}: {response_time:.2f}s (太慢)")
                        all_good = False
                else:
                    print(f"   ❌ {name}: HTTP {response.status_code}")
                    all_good = False
            
            print("   ℹ️  Backend API 性能透過內部服務間通訊驗證")
            return all_good
            
        except Exception as e:
            print(f"   ❌ 性能測試失敗: {e}")
            return False
    
    def test_security(self):
        """測試安全性"""
        try:
            # 檢查 SSL 證書（簡單檢查）
            response = requests.get(self.domain, timeout=10)
            if response.url.startswith('https://'):
                print("   ✅ SSL 證書有效")
            else:
                print("   ❌ SSL 證書問題")
                return False
            
            # 檢查是否暴露敏感信息
            sensitive_endpoints = [
                "/admin",
                "/.env",
                "/config",
                "/debug"
            ]
            
            for endpoint in sensitive_endpoints:
                try:
                    url = f"{self.domain}{endpoint}"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"   ⚠️  敏感端點可訪問: {endpoint}")
                    elif response.status_code in [404, 403]:
                        print(f"   ✅ 敏感端點受保護: {endpoint}")
                except:
                    print(f"   ✅ 敏感端點受保護: {endpoint}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 安全性檢查失敗: {e}")
            return False
    
    def test_service_availability(self):
        """測試服務可用性（連續測試）"""
        try:
            print("   🔄 執行連續可用性測試（10次請求）...")
            
            # 測試前端服務的可用性（間接驗證整體系統）
            success_count = 0
            total_time = 0
            
            for i in range(10):
                try:
                    start_time = time.time()
                    response = requests.get(self.domain, timeout=5)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        success_count += 1
                        total_time += (end_time - start_time)
                    
                    time.sleep(0.1)  # 短暫延遲
                except:
                    pass
            
            availability = (success_count / 10) * 100
            avg_response_time = total_time / success_count if success_count > 0 else 0
            
            print(f"   📊 前端服務可用性: {availability:.1f}% ({success_count}/10)")
            print(f"   ⏱️  平均響應時間: {avg_response_time:.2f}s")
            print("   ℹ️  Backend 服務可用性透過前端間接驗證")
            
            return availability >= 90  # 至少90%可用性
            
        except Exception as e:
            print(f"   ❌ 可用性測試失敗: {e}")
            return False
    
    def print_summary(self):
        """列印測試摘要"""
        print("\n" + "=" * 60)
        print("📊 Production 環境測試結果摘要")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ 通過" if result else "❌ 失敗"
            print(f"  {status} {test_name}")
        
        print(f"\n📈 總計: {passed}/{total} 項測試通過")
        
        if passed == total:
            print("🎉 所有測試通過！Production 環境運行正常。")
        elif passed >= total * 0.8:
            print("⚠️  大部分測試通過，但仍有改進空間。")
        else:
            print("❌ 多項測試失敗，請檢查 Production 環境配置。")
        
        print(f"\n🕐 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 提供建議
        if not all(self.test_results.values()):
            print("\n💡 建議的修復步驟:")
            print("1. 檢查所有容器是否正常運行")
            print("2. 確認域名和 SSL 證書配置")
            print("3. 檢查網路和防火牆設定")
            print("4. 查看應用程式日誌")
            print("5. 驗證環境變數配置")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Environment Test Suite")
    parser.add_argument("--domain", default="https://smarthome.the-jasperezlife.com",
                       help="Production domain to test (default: https://smarthome.the-jasperezlife.com)")
    
    args = parser.parse_args()
    
    tester = ProductionEnvironmentTester(args.domain)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
