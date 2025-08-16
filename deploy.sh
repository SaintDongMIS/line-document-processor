#!/bin/bash

# 快速部署腳本 - 一鍵部署 LINE Webhook 接收器

echo "🚀 快速部署 LINE Webhook 接收器..."

# 檢查必要檔案
if [ ! -f "webhook_receiver/.env.yaml" ]; then
    echo "❌ 錯誤: webhook_receiver/.env.yaml 不存在"
    echo "請先複製 .env.yaml.example 並填入您的設定"
    exit 1
fi

# 顯示當前配置
echo "📋 當前配置:"
gcloud config list --format="value(core.project,core.account)" 2>/dev/null || echo "未設定"

# 部署
echo "📤 部署中..."
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

# 取得 Webhook URL
WEBHOOK_URL=$(gcloud functions describe line-webhook-receiver --format="value(httpsTrigger.url)")
echo ""
echo "✅ 部署完成！"
echo "🌐 Webhook URL: $WEBHOOK_URL"
echo ""
echo "📋 下一步: 在 LINE Developer Console 設定 Webhook URL"
echo "🔗 查看日誌: gcloud functions logs read line-webhook-receiver"
