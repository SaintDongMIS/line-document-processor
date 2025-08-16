#!/bin/bash

# LINE 文件處理系統部署腳本

set -e  # 遇到錯誤時停止執行

echo "🚀 開始部署 LINE 文件處理系統..."

# 檢查必要的環境變數
if [ -z "$GCP_PROJECT" ]; then
    echo "❌ 錯誤: 請設定 GCP_PROJECT 環境變數"
    exit 1
fi

if [ -z "$BUCKET_NAME" ]; then
    echo "❌ 錯誤: 請設定 BUCKET_NAME 環境變數"
    exit 1
fi

echo "📋 部署資訊:"
echo "  專案 ID: $GCP_PROJECT"
echo "  原始檔案 Bucket: $BUCKET_NAME"
echo "  處理後檔案 Bucket: $PROCESSED_BUCKET_NAME"

# 設定 GCP 專案
echo "🔧 設定 GCP 專案..."
gcloud config set project $GCP_PROJECT

# 啟用必要的 API
echo "🔌 啟用必要的 GCP API..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable documentai.googleapis.com
gcloud services enable storage.googleapis.com

# 建立 GCS Bucket (如果不存在)
echo "📦 檢查並建立 GCS Bucket..."
if ! gsutil ls -b gs://$BUCKET_NAME > /dev/null 2>&1; then
    echo "建立原始檔案 Bucket: $BUCKET_NAME"
    gsutil mb gs://$BUCKET_NAME
fi

if [ ! -z "$PROCESSED_BUCKET_NAME" ]; then
    if ! gsutil ls -b gs://$PROCESSED_BUCKET_NAME > /dev/null 2>&1; then
        echo "建立處理後檔案 Bucket: $PROCESSED_BUCKET_NAME"
        gsutil mb gs://$PROCESSED_BUCKET_NAME
    fi
fi

# 部署 Webhook 接收器
echo "📤 部署 LINE Webhook 接收器..."
gcloud functions deploy line-webhook-receiver \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --source webhook_receiver \
    --entry-point line_webhook \
    --set-env-vars GCP_PROJECT=$GCP_PROJECT,BUCKET_NAME=$BUCKET_NAME \
    --region us-central1 \
    --memory 512MB \
    --timeout 60s

# 取得 Webhook URL
WEBHOOK_URL=$(gcloud functions describe line-webhook-receiver --region=us-central1 --format="value(httpsTrigger.url)")
echo "✅ Webhook 接收器已部署: $WEBHOOK_URL"

# 部署文件處理器
echo "📤 部署文件處理器..."
gcloud functions deploy document-processor \
    --runtime python39 \
    --trigger-event google.storage.object.finalize \
    --trigger-resource $BUCKET_NAME \
    --source document_processor \
    --entry-point process_document \
    --set-env-vars GCP_PROJECT=$GCP_PROJECT,PROCESSED_BUCKET_NAME=$PROCESSED_BUCKET_NAME \
    --region us-central1 \
    --memory 1024MB \
    --timeout 540s

echo "✅ 文件處理器已部署"

# 設定 IAM 權限
echo "🔐 設定 IAM 權限..."
gcloud projects add-iam-policy-binding $GCP_PROJECT \
    --member="serviceAccount:$GCP_PROJECT@appspot.gserviceaccount.com" \
    --role="roles/documentai.apiUser"

echo "🎉 部署完成！"
echo ""
echo "📋 後續步驟:"
echo "1. 在 LINE Developer Console 中設定 Webhook URL: $WEBHOOK_URL"
echo "2. 設定 LINE Channel Access Token 環境變數"
echo "3. 設定 Document AI Processor ID 環境變數"
echo "4. 測試系統功能"
echo ""
echo "🔗 有用的指令:"
echo "  查看日誌: gcloud functions logs read line-webhook-receiver"
echo "  查看日誌: gcloud functions logs read document-processor"
echo "  刪除函式: gcloud functions delete line-webhook-receiver"
echo "  刪除函式: gcloud functions delete document-processor"
