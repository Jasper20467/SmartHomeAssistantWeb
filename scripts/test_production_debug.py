#!/usr/bin/env python3
"""
Production 環境診斷腳本

診斷 production 環境下的問題
"""

import requests
import time
from datetime import datetime

def check_production_status():
    """檢查 production 環境狀態"""
    print("🚀 Production 環境診斷")
    print("=" * 50)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目標: https://smarthome.the-jasperezlife.com")
    print()
    
    # 檢查前端
    print("🌐 檢查前端...")
    try:
        response = requests.get("https://smarthome.the-jasperezlife.com", timeout=10)
        if response.status_code == 200:
            print("   ✅ 前端正常運行")
        else:
            print(f"   ❌ 前端異常: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 前端錯誤: {e}")
    
    # 檢查 API 端點
    print("\n🔌 檢查 API 端點...")
    api_endpoints = [
        "/api/health",
        "/api/schedules/",
        "/api/consumables/"
    ]
    
    for endpoint in api_endpoints:
        try:
            url = f"https://smarthome.the-jasperezlife.com{endpoint}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: HTTP {response.status_code}")
            elif response.status_code == 502:
                print(f"   ❌ {endpoint}: HTTP 502 (Backend 連接失敗)")
            else:
                print(f"   ⚠️  {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
    
    # 檢查 LineBot 健康端點
    print("\n🤖 檢查 LineBot...")
    try:
        response = requests.get("https://smarthome.the-jasperezlife.com/linebot/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ LineBot 正常運行")
        else:
            print(f"   ❌ LineBot 異常: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ LineBot 錯誤: {e}")

def check_debug_comparison():
    """對比 debug 環境狀態"""
    print("\n🐛 對比 Debug 環境...")
    try:
        response = requests.get("http://localhost/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Debug 環境 Backend 正常")
        else:
            print(f"   ❌ Debug 環境 Backend 異常: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Debug 環境無法連接: {e}")

if __name__ == "__main__":
    check_production_status()
    check_debug_comparison()
    
    print("\n" + "=" * 50)
    print("📋 診斷完成")
    print("\n💡 建議的修復步驟:")
    print("1. 檢查 backend 容器是否正常運行")
    print("2. 確認 backend 映像檔版本是否包含最新修復")
    print("3. 檢查 backend 容器日誌")
    print("4. 重新建置並推送最新的 backend 映像檔")
