#!/bin/bash

# LINE Webhook 接收器管理腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

FUNCTION_NAME="line-webhook-receiver"

show_help() {
    echo "🚀 LINE Webhook 接收器管理腳本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy     - 部署 Cloud Function"
    echo "  logs       - 查看日誌"
    echo "  status     - 查看函式狀態"
    echo "  test       - 測試健康檢查"
    echo "  delete     - 刪除 Cloud Function"
    echo "  url        - 顯示 Webhook URL"
    echo "  help       - 顯示此說明"
    echo ""
    echo "範例:"
    echo "  $0 deploy    # 部署函式"
    echo "  $0 logs      # 查看日誌"
    echo "  $0 test      # 測試健康檢查"
}

deploy_function() {
    print_info "部署 Cloud Function..."
    
    if [ ! -f "webhook_receiver/.env.yaml" ]; then
        print_error "webhook_receiver/.env.yaml 不存在"
        echo "請先複製 .env.yaml.example 並填入您的設定"
        exit 1
    fi
    
    gcloud functions deploy $FUNCTION_NAME \
        --runtime python311 \
        --trigger-http \
        --allow-unauthenticated \
        --source webhook_receiver \
        --entry-point line_webhook \
        --env-vars-file webhook_receiver/.env.yaml \
        --memory 256MB \
        --timeout 60s \
        --region asia-east1
    
    print_success "部署完成！"
    show_webhook_url
}

show_logs() {
    print_info "查看 Cloud Function 日誌..."
    gcloud functions logs read $FUNCTION_NAME --limit=20
}

show_status() {
    print_info "Cloud Function 狀態:"
    gcloud functions describe $FUNCTION_NAME --format="table(name,status,updateTime,httpsTrigger.url)"
}

test_health() {
    local url=$(gcloud functions describe $FUNCTION_NAME --format="value(httpsTrigger.url)" 2>/dev/null)
    
    if [ -z "$url" ]; then
        print_error "無法取得 Webhook URL，函式可能未部署"
        exit 1
    fi
    
    print_info "測試健康檢查: $url"
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        print_success "健康檢查通過！"
    else
        print_error "健康檢查失敗"
        echo "回應內容:"
        curl -s "$url" || echo "無法連接到函式"
    fi
}

delete_function() {
    print_warning "即將刪除 Cloud Function: $FUNCTION_NAME"
    read -p "確定要刪除嗎？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud functions delete $FUNCTION_NAME --region=us-central1
        print_success "Cloud Function 已刪除"
    else
        print_info "取消刪除"
    fi
}

show_webhook_url() {
    local url=$(gcloud functions describe $FUNCTION_NAME --format="value(httpsTrigger.url)" 2>/dev/null)
    
    if [ -z "$url" ]; then
        print_error "無法取得 Webhook URL"
        return 1
    fi
    
    echo ""
    print_info "Webhook URL:"
    echo "$url"
    echo ""
    echo "請將此 URL 設定到 LINE Developer Console 的 Webhook URL"
}

# 主程式
case "${1:-help}" in
    deploy)
        deploy_function
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    test)
        test_health
        ;;
    delete)
        delete_function
        ;;
    url)
        show_webhook_url
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
