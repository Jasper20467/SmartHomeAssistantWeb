#!/usr/bin/env python3
"""
Production Mode 配置驗證腳本

驗證生產模式下的配置是否正確，包括：
- Docker Compose 配置
- 環境變數設定
- 網路配置
- 服務依賴關係
"""

import os
import sys
import json
from pathlib import Path

def read_yaml_simple(file_path):
    """簡單的 YAML 讀取（僅用於基本檢查）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"讀取檔案失敗: {e}")
        return None

def validate_production_compose():
    """驗證生產模式 Docker Compose 配置"""
    print("🔍 驗證生產模式 Docker Compose 配置...")
    
    compose_file = Path("../scripts/DeployOn_AWS_Ec2/docker-compose_fromHub.yml")
    if not compose_file.exists():
        print(f"   ❌ 找不到生產模式配置檔案: {compose_file}")
        return False
    
    try:
        with open(compose_file, 'r', encoding='utf-8') as f:
            compose_content = f.read()
        
        # 簡單的文本檢查
        required_services = ['frontend:', 'backend:', 'linebot:', 'db:', 'caddy:']
        missing_services = []
        
        for service in required_services:
            if service not in compose_content:
                missing_services.append(service.replace(':', ''))
        
        if missing_services:
            print(f"   ❌ 缺少必要服務: {missing_services}")
            return False
        
        print("   ✅ 所有必要服務已定義")
        
        # 檢查網路配置
        if 'networks:' not in compose_content:
            print("   ❌ 未定義網路配置")
            return False
        
        if 'app-network:' not in compose_content:
            print("   ❌ 未定義 app-network")
            return False
        
        # 檢查每個服務是否都加入了 app-network
        service_sections = ['frontend:', 'backend:', 'linebot:', 'db:', 'caddy:']
        for service in service_sections:
            service_start = compose_content.find(service)
            if service_start == -1:
                continue
            
            # 找到下一個服務的開始位置
            next_service_start = len(compose_content)
            for other_service in service_sections:
                if other_service == service:
                    continue
                other_start = compose_content.find(other_service, service_start + 1)
                if other_start != -1 and other_start < next_service_start:
                    next_service_start = other_start
            
            service_content = compose_content[service_start:next_service_start]
            
            if 'networks:' not in service_content:
                print(f"   ❌ 服務 {service.replace(':', '')} 未加入網路")
                return False
            
            if 'app-network' not in service_content:
                print(f"   ❌ 服務 {service.replace(':', '')} 未加入 app-network")
                return False
        
        print("   ✅ 網路配置正確")
        
        # 檢查 backend 的資料庫 URL
        if 'DATABASE_URL=postgresql+asyncpg://' not in compose_content:
            print("   ❌ Backend 資料庫 URL 未使用 async driver")
            return False
        
        print("   ✅ Backend 資料庫 URL 使用正確的 async driver")
        
        # 檢查 linebot 的環境變數
        if 'DEBUG_MODE=false' not in compose_content:
            print("   ❌ LineBot DEBUG_MODE 應設為 false")
            return False
        
        if 'DEBUG_STAGE=false' not in compose_content:
            print("   ❌ LineBot DEBUG_STAGE 應設為 false")
            return False
        
        if 'DOMAIN_NAME=' not in compose_content:
            print("   ❌ LineBot 未設定 DOMAIN_NAME")
            return False
        
        print("   ✅ LineBot 環境變數配置正確")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 驗證失敗: {e}")
        return False

def validate_debug_compose():
    """驗證除錯模式 Docker Compose 配置"""
    print("🔍 驗證除錯模式 Docker Compose 配置...")
    
    compose_file = Path("../docker-compose.yml")
    if not compose_file.exists():
        print(f"   ❌ 找不到除錯模式配置檔案: {compose_file}")
        return False
    
    try:
        with open(compose_file, 'r', encoding='utf-8') as f:
            compose_content = f.read()
        
        # 簡單的文本檢查
        required_services = ['frontend:', 'backend:', 'linebot:', 'db:']
        missing_services = []
        
        for service in required_services:
            if service not in compose_content:
                missing_services.append(service.replace(':', ''))
        
        if missing_services:
            print(f"   ❌ 缺少必要服務: {missing_services}")
            return False
        
        print("   ✅ 所有必要服務已定義")
        
        # 檢查網路配置
        if 'networks:' not in compose_content:
            print("   ❌ 未定義網路配置")
            return False
        
        if 'app-network:' not in compose_content:
            print("   ❌ 未定義 app-network")
            return False
        
        # 檢查每個服務是否都加入了 app-network
        service_sections = ['frontend:', 'backend:', 'linebot:', 'db:']
        for service in service_sections:
            service_start = compose_content.find(service)
            if service_start == -1:
                continue
            
            # 找到下一個服務的開始位置
            next_service_start = len(compose_content)
            for other_service in service_sections:
                if other_service == service:
                    continue
                other_start = compose_content.find(other_service, service_start + 1)
                if other_start != -1 and other_start < next_service_start:
                    next_service_start = other_start
            
            service_content = compose_content[service_start:next_service_start]
            
            if 'networks:' not in service_content:
                print(f"   ❌ 服務 {service.replace(':', '')} 未加入網路")
                return False
            
            if 'app-network' not in service_content:
                print(f"   ❌ 服務 {service.replace(':', '')} 未加入 app-network")
                return False
        
        print("   ✅ 網路配置正確")
        
        # 檢查 backend 的資料庫 URL
        if 'DATABASE_URL=postgresql+asyncpg://' not in compose_content:
            print("   ❌ Backend 資料庫 URL 未使用 async driver")
            return False
        
        print("   ✅ Backend 資料庫 URL 使用正確的 async driver")
        
        # 檢查 linebot 的環境變數
        if 'DEBUG_MODE=true' not in compose_content:
            print("   ❌ LineBot DEBUG_MODE 應設為 true")
            return False
        
        if 'DEBUG_STAGE=true' not in compose_content:
            print("   ❌ LineBot DEBUG_STAGE 應設為 true")
            return False
        
        if 'DOMAIN_NAME=localhost' not in compose_content:
            print("   ❌ LineBot DOMAIN_NAME 應設為 localhost")
            return False
        
        print("   ✅ LineBot 環境變數配置正確")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 驗證失敗: {e}")
        return False

def validate_frontend_configs():
    """驗證前端配置"""
    print("🔍 驗證前端環境配置...")
    
    # 檢查 development 環境配置
    dev_config = Path("../frontend/src/environments/environment.ts")
    if not dev_config.exists():
        print("   ❌ 找不到開發環境配置檔案")
        return False
    
    try:
        with open(dev_config, 'r', encoding='utf-8') as f:
            dev_content = f.read()
        
        if 'http://localhost:8000/api' not in dev_content:
            print("   ❌ 開發環境配置未使用 localhost:8000")
            return False
        
        print("   ✅ 開發環境配置正確")
        
    except Exception as e:
        print(f"   ❌ 驗證開發環境配置失敗: {e}")
        return False
    
    # 檢查 production 環境配置
    prod_config = Path("../frontend/src/environments/environment.prod.ts")
    if not prod_config.exists():
        print("   ❌ 找不到生產環境配置檔案")
        return False
    
    try:
        with open(prod_config, 'r', encoding='utf-8') as f:
            prod_content = f.read()
        
        if "'/api'" not in prod_content:
            print("   ❌ 生產環境配置未使用相對路徑")
            return False
        
        print("   ✅ 生產環境配置正確")
        
    except Exception as e:
        print(f"   ❌ 驗證生產環境配置失敗: {e}")
        return False
    
    return True

def validate_caddy_config():
    """驗證 Caddy 配置"""
    print("🔍 驗證 Caddy 配置...")
    
    caddy_file = Path("../scripts/DeployOn_AWS_Ec2/Caddyfile")
    if not caddy_file.exists():
        print("   ❌ 找不到 Caddyfile")
        return False
    
    try:
        with open(caddy_file, 'r', encoding='utf-8') as f:
            caddy_content = f.read()
        
        # 檢查基本配置
        if 'smarthome.the-jasperezlife.com' not in caddy_content:
            print("   ❌ 未設定正確的域名")
            return False
        
        # 檢查 API 代理
        if 'reverse_proxy @api backend:8000' not in caddy_content:
            print("   ❌ API 代理配置不正確")
            return False
        
        # 檢查 LineBot 代理
        if 'reverse_proxy @linebot linebot:5000' not in caddy_content:
            print("   ❌ LineBot 代理配置不正確")
            return False
        
        # 檢查前端代理
        if 'reverse_proxy frontend:80' not in caddy_content:
            print("   ❌ 前端代理配置不正確")
            return False
        
        print("   ✅ Caddy 配置正確")
        return True
        
    except Exception as e:
        print(f"   ❌ 驗證 Caddy 配置失敗: {e}")
        return False

def main():
    """主程式"""
    print("🏠 Smart Home Assistant 配置驗證")
    print("=" * 60)
    
    results = []
    
    # 驗證除錯模式配置
    print("\n🐛 除錯模式配置驗證")
    print("-" * 40)
    results.append(validate_debug_compose())
    
    # 驗證生產模式配置
    print("\n🚀 生產模式配置驗證")
    print("-" * 40)
    results.append(validate_production_compose())
    
    # 驗證前端配置
    print("\n🌐 前端配置驗證")
    print("-" * 40)
    results.append(validate_frontend_configs())
    
    # 驗證 Caddy 配置
    print("\n🔄 Caddy 配置驗證")
    print("-" * 40)
    results.append(validate_caddy_config())
    
    # 結果摘要
    print("\n" + "=" * 60)
    print("📊 配置驗證結果摘要")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ 通過: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 配置狀態: 優秀")
        return True
    elif success_rate >= 80:
        print("✅ 配置狀態: 良好")
        return True
    elif success_rate >= 60:
        print("⚠️  配置狀態: 需要改進")
        return False
    else:
        print("❌ 配置狀態: 需要修復")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if main():
        print("\n✅ 配置驗證完成 - 所有配置正確")
        sys.exit(0)
    else:
        print("\n❌ 配置驗證完成 - 發現問題，請檢查")
        sys.exit(1)
