#!/bin/bash

# LINE Webhook 接收器部署腳本 (優化版)

set -e  # 遇到錯誤時停止執行

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函式定義
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 檢查 gcloud 是否已安裝
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI 未安裝或不在 PATH 中"
        echo "請先安裝 Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
}

# 檢查 GCP 認證
check_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "未找到有效的 GCP 認證"
        echo "請先執行: gcloud auth login"
        exit 1
    fi
}

# 檢查必要檔案
check_files() {
    local missing_files=()
    
    if [ ! -f "webhook_receiver/.env.yaml" ]; then
        missing_files+=("webhook_receiver/.env.yaml")
    fi
    
    if [ ! -f "webhook_receiver/main.py" ]; then
        missing_files+=("webhook_receiver/main.py")
    fi
    
    if [ ! -f "webhook_receiver/requirements.txt" ]; then
        missing_files+=("webhook_receiver/requirements.txt")
    fi
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        print_error "缺少必要檔案:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
}

# 顯示當前配置
show_config() {
    print_info "當前 GCP 配置:"
    local project=$(gcloud config get-value project 2>/dev/null || echo "未設定")
    local account=$(gcloud config get-value account 2>/dev/null || echo "未設定")
    echo "  專案: $project"
    echo "  帳號: $account"
    echo ""
}

# 確認部署
confirm_deployment() {
    print_warning "即將部署 LINE Webhook 接收器到 GCP Cloud Functions"
    echo ""
    show_config
    echo "這將會:"
    echo "  - 部署 Cloud Function: line-webhook-receiver"
    echo "  - 使用 Python 3.11 runtime"
    echo "  - 設定 HTTP 觸發器"
    echo "  - 允許未認證存取"
    echo ""
    
    read -p "是否繼續部署？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "部署已取消"
        exit 0
    fi
}

# 部署 Cloud Function
deploy_function() {
    print_info "開始部署 Cloud Function..."
    
    gcloud functions deploy line-webhook-receiver \
        --runtime python311 \
        --trigger-http \
        --allow-unauthenticated \
        --source webhook_receiver \
        --entry-point line_webhook \
        --env-vars-file webhook_receiver/.env.yaml \
        --memory 256MB \
        --timeout 60s \
        --region asia-east1
    
    print_success "Cloud Function 部署完成！"
}

# 取得並顯示 Webhook URL
get_webhook_url() {
    local webhook_url=$(gcloud functions describe line-webhook-receiver --format="value(httpsTrigger.url)" 2>/dev/null)
    
    if [ -z "$webhook_url" ]; then
        print_error "無法取得 Webhook URL"
        return 1
    fi
    
    echo ""
    print_success "部署完成！"
    echo "🌐 Webhook URL: $webhook_url"
    echo ""
    
    # 測試健康檢查
    print_info "測試健康檢查..."
    if curl -s -f "$webhook_url" > /dev/null 2>&1; then
        print_success "健康檢查通過！"
    else
        print_warning "健康檢查失敗，可能需要等待幾分鐘讓函式完全啟動"
    fi
    
    return 0
}

# 顯示後續步驟
show_next_steps() {
    local webhook_url=$(gcloud functions describe line-webhook-receiver --format="value(httpsTrigger.url)" 2>/dev/null)
    
    echo ""
    print_info "📋 後續步驟:"
    echo "1. 在 LINE Developer Console 中設定 Webhook URL:"
    echo "   $webhook_url"
    echo ""
    echo "2. 測試功能:"
    echo "   - 在 LINE 中傳送圖片或檔案"
    echo "   - 檢查 Cloud Storage 是否收到檔案"
    echo ""
    print_info "🔗 有用的指令:"
    echo "  查看日誌: gcloud functions logs read line-webhook-receiver"
    echo "  查看函式: gcloud functions describe line-webhook-receiver"
    echo "  測試健康檢查: curl -X GET \"$webhook_url\""
    echo "  刪除函式: gcloud functions delete line-webhook-receiver"
    echo ""
}

# 主程式
main() {
    echo "🚀 LINE Webhook 接收器部署腳本"
    echo "=================================="
    echo ""
    
    # 檢查前置條件
    check_gcloud
    check_auth
    check_files
    
    # 確認部署
    confirm_deployment
    
    # 執行部署
    deploy_function
    
    # 取得 Webhook URL
    if get_webhook_url; then
        show_next_steps
    fi
}

# 執行主程式
main "$@"
