#!/usr/bin/env python3
"""
測試環境變數載入
"""

import os
from dotenv import load_dotenv

print("🔍 測試環境變數載入...")

# 載入 .env.local 檔案
env_file = '.env.local'
if os.path.exists(env_file):
    print(f"✅ 找到 {env_file} 檔案")
    load_dotenv(env_file)
    
    # 測試讀取環境變數
    print(f"🌍 環境: {os.getenv('ENVIRONMENT', '未設定')}")
    print(f"🔧 專案 ID: {os.getenv('GCP_PROJECT', '未設定')}")
    print(f"📦 原始檔案 Bucket: {os.getenv('BUCKET_NAME', '未設定')}")
    print(f"🔑 LINE Token: {os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '未設定')[:20]}...")
    print(f"👤 用戶 ID: {os.getenv('LINE_USER_ID_SAM', '未設定')}")
    print(f"🐛 Debug 模式: {os.getenv('DEBUG', '未設定')}")
    
else:
    print("❌ 找不到 .env.local 檔案")
    print("當前目錄檔案:")
    for file in os.listdir('.'):
        if file.startswith('.env'):
            print(f"  - {file}")
