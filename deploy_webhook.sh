#!/bin/bash

# LINE Webhook 接收器部署腳本 (簡化版)

set -e  # 遇到錯誤時停止執行

echo "🚀 開始部署 LINE Webhook 接收器..."

# 檢查當前 GCP 配置
echo "📋 當前 GCP 配置:"
gcloud config list --format="value(core.project,core.account)"

# 確認部署
read -p "是否繼續部署？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

# 檢查必要檔案
if [ ! -f "webhook_receiver/.env.yaml" ]; then
    echo "❌ 錯誤: webhook_receiver/.env.yaml 不存在"
    echo "請先設定環境變數檔案"
    exit 1
fi

if [ ! -f "webhook_receiver/main.py" ]; then
    echo "❌ 錯誤: webhook_receiver/main.py 不存在"
    exit 1
fi

# 部署 Cloud Function
echo "📤 部署 LINE Webhook 接收器..."
gcloud functions deploy line-webhook-receiver \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --source webhook_receiver \
    --entry-point line_webhook \
    --env-vars-file webhook_receiver/.env.yaml

# 取得 Webhook URL
WEBHOOK_URL=$(gcloud functions describe line-webhook-receiver --format="value(httpsTrigger.url)")
echo ""
echo "✅ 部署完成！"
echo "🌐 Webhook URL: $WEBHOOK_URL"
echo ""
echo "📋 後續步驟:"
echo "1. 在 LINE Developer Console 中設定 Webhook URL: $WEBHOOK_URL"
echo "2. 測試圖片下載功能"
echo ""
echo "🔗 有用的指令:"
echo "  查看日誌: gcloud functions logs read line-webhook-receiver"
echo "  測試健康檢查: curl -X GET \"$WEBHOOK_URL\""
echo "  刪除函式: gcloud functions delete line-webhook-receiver"
