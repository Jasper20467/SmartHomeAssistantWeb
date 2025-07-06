#!/bin/bash

# Smart Home Assistant Docker Images Build and Push Script
# 自動建置並推送所有 Docker 映像到 Docker Hub
# 
# 使用方法：
# ./push_docker_images.sh [版本號]
# 
# 範例：
# ./push_docker_images.sh 1.1
# ./push_docker_images.sh latest

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Docker Hub 設定
DOCKER_USERNAME="popo510691"
REGISTRY="docker.io"

# 映像名稱配置
declare -A IMAGES
IMAGES=(
    ["frontend"]="homeassistant.frontend"
    ["backend"]="homeassistant.backend"
    ["linebot"]="homeassistant.linebot"
)

# Dockerfile 路徑配置
declare -A DOCKERFILES
DOCKERFILES=(
    ["frontend"]="docker/frontend.Dockerfile"
    ["backend"]="docker/backend.Dockerfile"
    ["linebot"]="docker/linebot.Dockerfile"
)

# 建置上下文配置
declare -A BUILD_CONTEXTS
BUILD_CONTEXTS=(
    ["frontend"]="./frontend"
    ["backend"]="./backend"
    ["linebot"]="."
)

# 顯示標題
echo -e "${PURPLE}=================================================${NC}"
echo -e "${PURPLE}  Smart Home Assistant Docker Build & Push${NC}"
echo -e "${PURPLE}=================================================${NC}"
echo

# 檢查參數
VERSION=${1:-"latest"}
echo -e "${BLUE}📦 建置版本：${NC}${VERSION}"
echo

# 檢查是否已登入 Docker Hub
echo -e "${YELLOW}🔐 檢查 Docker Hub 登入狀態...${NC}"
if ! docker info | grep -q "Username: $DOCKER_USERNAME"; then
    echo -e "${RED}❌ 尚未登入 Docker Hub，請先執行：${NC}"
    echo -e "${CYAN}docker login${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 已登入 Docker Hub (用戶: $DOCKER_USERNAME)${NC}"
echo

# 檢查 Docker 是否運行
echo -e "${YELLOW}🐳 檢查 Docker 服務...${NC}"
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker 服務未運行，請先啟動 Docker${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker 服務正常運行${NC}"
echo

# 檢查必要檔案
echo -e "${YELLOW}📁 檢查必要檔案...${NC}"
for service in "${!DOCKERFILES[@]}"; do
    dockerfile="${DOCKERFILES[$service]}"
    context="${BUILD_CONTEXTS[$service]}"
    
    if [[ ! -f "$dockerfile" ]]; then
        echo -e "${RED}❌ Dockerfile 不存在: $dockerfile${NC}"
        exit 1
    fi
    
    if [[ ! -d "$context" ]]; then
        echo -e "${RED}❌ 建置上下文目錄不存在: $context${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ 所有必要檔案都存在${NC}"
echo

# 清理舊的映像（可選）
echo -e "${YELLOW}🧹 是否要清理舊的本地映像？(y/N): ${NC}"
read -r -n 1 CLEANUP
echo
if [[ $CLEANUP =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 清理舊的本地映像...${NC}"
    for service in "${!IMAGES[@]}"; do
        image_name="$DOCKER_USERNAME/${IMAGES[$service]}"
        docker rmi "$image_name:latest" 2>/dev/null || true
        docker rmi "$image_name:$VERSION" 2>/dev/null || true
    done
    echo -e "${GREEN}✅ 清理完成${NC}"
fi
echo

# 建置和推送函數
build_and_push() {
    local service=$1
    local image_name="$DOCKER_USERNAME/${IMAGES[$service]}"
    local dockerfile="${DOCKERFILES[$service]}"
    local context="${BUILD_CONTEXTS[$service]}"
    
    echo -e "${PURPLE}🏗️  建置 $service 映像...${NC}"
    echo -e "${CYAN}   映像名稱: $image_name:$VERSION${NC}"
    echo -e "${CYAN}   Dockerfile: $dockerfile${NC}"
    echo -e "${CYAN}   建置上下文: $context${NC}"
    
    # 建置映像
    if docker build -f "$dockerfile" -t "$image_name:$VERSION" "$context"; then
        echo -e "${GREEN}✅ $service 建置成功${NC}"
        
        # 如果版本不是 latest，也標記為 latest
        if [[ "$VERSION" != "latest" ]]; then
            docker tag "$image_name:$VERSION" "$image_name:latest"
            echo -e "${GREEN}✅ 已標記為 latest${NC}"
        fi
        
        # 推送映像
        echo -e "${YELLOW}📤 推送 $service 映像到 Docker Hub...${NC}"
        if docker push "$image_name:$VERSION"; then
            echo -e "${GREEN}✅ $service 推送成功${NC}"
            
            # 推送 latest 標籤
            if [[ "$VERSION" != "latest" ]]; then
                docker push "$image_name:latest"
                echo -e "${GREEN}✅ $service latest 標籤推送成功${NC}"
            fi
        else
            echo -e "${RED}❌ $service 推送失敗${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ $service 建置失敗${NC}"
        return 1
    fi
    echo
}

# 顯示建置計劃
echo -e "${BLUE}📋 建置計劃：${NC}"
for service in "${!IMAGES[@]}"; do
    image_name="$DOCKER_USERNAME/${IMAGES[$service]}"
    echo -e "${CYAN}   • $service -> $image_name:$VERSION${NC}"
done
echo

# 確認開始建置
echo -e "${YELLOW}🚀 是否開始建置並推送所有映像？(Y/n): ${NC}"
read -r -n 1 CONFIRM
echo
if [[ $CONFIRM =~ ^[Nn]$ ]]; then
    echo -e "${YELLOW}⏹️  作業已取消${NC}"
    exit 0
fi

# 記錄開始時間
START_TIME=$(date +%s)

# 建置所有映像
echo -e "${PURPLE}🚀 開始建置和推送所有映像...${NC}"
echo

FAILED_SERVICES=()
SUCCESSFUL_SERVICES=()

for service in "${!IMAGES[@]}"; do
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}處理服務: $service${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if build_and_push "$service"; then
        SUCCESSFUL_SERVICES+=("$service")
    else
        FAILED_SERVICES+=("$service")
        echo -e "${RED}❌ $service 處理失敗，繼續處理下一個服務...${NC}"
    fi
done

# 計算執行時間
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# 顯示總結
echo -e "${PURPLE}=================================================${NC}"
echo -e "${PURPLE}  建置和推送完成總結${NC}"
echo -e "${PURPLE}=================================================${NC}"
echo
echo -e "${BLUE}⏱️  總執行時間: ${MINUTES}分${SECONDS}秒${NC}"
echo -e "${BLUE}📦 目標版本: $VERSION${NC}"
echo

if [[ ${#SUCCESSFUL_SERVICES[@]} -gt 0 ]]; then
    echo -e "${GREEN}✅ 成功的服務 (${#SUCCESSFUL_SERVICES[@]})：${NC}"
    for service in "${SUCCESSFUL_SERVICES[@]}"; do
        image_name="$DOCKER_USERNAME/${IMAGES[$service]}"
        echo -e "${GREEN}   • $service -> $image_name:$VERSION${NC}"
    done
    echo
fi

if [[ ${#FAILED_SERVICES[@]} -gt 0 ]]; then
    echo -e "${RED}❌ 失敗的服務 (${#FAILED_SERVICES[@]})：${NC}"
    for service in "${FAILED_SERVICES[@]}"; do
        echo -e "${RED}   • $service${NC}"
    done
    echo
fi

# 顯示 Docker Hub 連結
if [[ ${#SUCCESSFUL_SERVICES[@]} -gt 0 ]]; then
    echo -e "${CYAN}🔗 Docker Hub 連結：${NC}"
    for service in "${SUCCESSFUL_SERVICES[@]}"; do
        image_name="${IMAGES[$service]}"
        echo -e "${CYAN}   • https://hub.docker.com/r/$DOCKER_USERNAME/$image_name${NC}"
    done
    echo
fi

# 顯示使用說明
echo -e "${YELLOW}📖 使用新映像：${NC}"
echo -e "${CYAN}   • 更新 docker-compose.yml 中的版本號為 $VERSION${NC}"
echo -e "${CYAN}   • 或執行：docker-compose pull 拉取最新映像${NC}"
echo

# 提供更新配置檔案的選項
if [[ ${#SUCCESSFUL_SERVICES[@]} -gt 0 ]] && [[ "$VERSION" != "latest" ]]; then
    echo -e "${YELLOW}🔄 是否要自動更新 AWS EC2 部署配置檔案的版本號？(y/N): ${NC}"
    read -r -n 1 UPDATE_CONFIG
    echo
    if [[ $UPDATE_CONFIG =~ ^[Yy]$ ]]; then
        CONFIG_FILE="scripts/DeployOn_AWS_Ec2/docker-compose_fromHub.yml"
        if [[ -f "$CONFIG_FILE" ]]; then
            echo -e "${YELLOW}🔄 更新配置檔案...${NC}"
            
            # 備份原檔案
            cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
            
            # 更新版本號
            for service in "${SUCCESSFUL_SERVICES[@]}"; do
                image_name="${IMAGES[$service]}"
                sed -i.tmp "s|$DOCKER_USERNAME/$image_name:[^[:space:]]*|$DOCKER_USERNAME/$image_name:$VERSION|g" "$CONFIG_FILE"
                rm -f "$CONFIG_FILE.tmp" 2>/dev/null || true
            done
            
            echo -e "${GREEN}✅ 配置檔案已更新：$CONFIG_FILE${NC}"
            echo -e "${YELLOW}💾 備份檔案：$CONFIG_FILE.backup${NC}"
        else
            echo -e "${RED}❌ 配置檔案不存在：$CONFIG_FILE${NC}"
        fi
    fi
fi

# 最終狀態
if [[ ${#FAILED_SERVICES[@]} -eq 0 ]]; then
    echo -e "${GREEN}🎉 所有映像建置和推送成功完成！${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  部分映像建置或推送失敗，請檢查上述錯誤訊息${NC}"
    exit 1
fi
