#!/bin/bash

# GCP 配置管理腳本 (安全版本)
# 用於快速切換不同的 GCP 專案和帳號

echo "=== GCP 配置管理工具 ==="
echo ""

# 顯示當前配置
echo "當前配置："
gcloud config configurations list
echo ""

# 切換配置
echo "請選擇要切換的配置："
echo "1) 切換到 default 配置"
echo "2) 切換到 line-document-processor 配置"
echo "3) 查看所有配置"
echo "4) 查看當前配置詳情"
echo "5) 退出"

read -p "請輸入選項 (1-5): " choice

case $choice in
    1)
        echo "切換到 default 配置..."
        gcloud config configurations activate default
        echo "✅ 已切換到 default 配置"
        ;;
    2)
        echo "切換到 line-document-processor 配置..."
        gcloud config configurations activate line-document-processor
        echo "✅ 已切換到 line-document-processor 配置"
        ;;
    3)
        echo "所有配置："
        gcloud config configurations list
        ;;
    4)
        echo "當前配置詳情："
        gcloud config list
        ;;
    5)
        echo "退出"
        exit 0
        ;;
    *)
        echo "❌ 無效選項"
        exit 1
        ;;
esac

echo ""
echo "✅ 配置切換完成"
