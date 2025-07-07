#!/usr/bin/env python3
"""
Test Suite Summary
測試套件摘要

快速檢查測試腳本狀態和提供使用建議
"""

import os
import sys
from pathlib import Path

def check_environment():
    """檢查環境狀態"""
    print("🏠 Smart Home Assistant Test Suite Status")
    print("=" * 50)
    
    # 檢查腳本存在性
    script_dir = Path(__file__).parent
    debug_script = script_dir / "test_debug_environment.py"
    production_script = script_dir / "test_production_environment.py"
    guide = script_dir / "testing_guide.md"
    
    print("📁 測試腳本狀態:")
    print(f"  ✅ Debug 測試腳本: {debug_script.exists()}")
    print(f"  ✅ Production 測試腳本: {production_script.exists()}")
    print(f"  ✅ 使用指南: {guide.exists()}")
    
    # 檢查 Docker 狀態
    print("\n🐳 Docker 狀態:")
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\\t{{.Status}}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # 有標題行
                print("  運行中的容器:")
                for line in lines[1:]:
                    if line.strip():
                        print(f"    {line}")
            else:
                print("  ⚠️  沒有運行中的容器")
        else:
            print("  ❌ Docker 未運行或無權限")
    except Exception as e:
        print(f"  ❌ Docker 檢查失敗: {e}")
    
    # 使用建議
    print("\n💡 使用建議:")
    print("  1. 開發環境測試:")
    print("     python scripts/test_debug_environment.py")
    print("  2. 生產環境測試:")
    print("     python scripts/test_production_environment.py")
    print("  3. 詳細說明:")
    print("     查看 scripts/testing_guide.md")
    
    print("\n🔧 快速修復:")
    print("  • 如果容器未運行: docker-compose up -d")
    print("  • 如果測試失敗: 查看具體錯誤訊息")
    print("  • 如果需要清理: docker-compose down --volumes")

if __name__ == "__main__":
    check_environment()
