#!/usr/bin/env python3
"""
本地測試腳本：模擬發送 LINE Webhook 請求
"""

import requests
import json
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_line_webhook():
    """測試 LINE Webhook 接收端"""
    
    # 測試用的 LINE Webhook 事件資料
    test_events = [
        # 測試檔案訊息
        {
            "events": [
                {
                    "type": "message",
                    "message": {
                        "id": "test-message-id-123",
                        "type": "file",
                        "fileName": "test-invoice.pdf",
                        "fileSize": 1024
                    },
                    "replyToken": "test-reply-token-123",
                    "source": {
                        "userId": "test-user-id",
                        "type": "user"
                    },
                    "timestamp": 1234567890
                }
            ],
            "destination": "test-destination"
        },
        # 測試圖片訊息
        {
            "events": [
                {
                    "type": "message",
                    "message": {
                        "id": "test-image-id-456",
                        "type": "image",
                        "contentProvider": {
                            "type": "line"
                        }
                    },
                    "replyToken": "test-reply-token-456",
                    "source": {
                        "userId": "test-user-id",
                        "type": "user"
                    },
                    "timestamp": 1234567890
                }
            ],
            "destination": "test-destination"
        },
        # 測試文字訊息
        {
            "events": [
                {
                    "type": "message",
                    "message": {
                        "id": "test-text-id-789",
                        "type": "text",
                        "text": "測試訊息"
                    },
                    "replyToken": "test-reply-token-789",
                    "source": {
                        "userId": "test-user-id",
                        "type": "user"
                    },
                    "timestamp": 1234567890
                }
            ],
            "destination": "test-destination"
        }
    ]
    
    # 發送請求到本地測試伺服器
    webhook_url = "http://localhost:8080/"
    
    try:
        print("發送測試 Webhook 請求...")
        print(f"目標 URL: {webhook_url}")
        
        # 測試所有類型的事件
        for i, test_event in enumerate(test_events, 1):
            event_type = test_event["events"][0]["message"]["type"]
            print(f"\n--- 測試 {i}: {event_type} 訊息 ---")
            print(f"測試資料: {json.dumps(test_event, indent=2, ensure_ascii=False)}")
            
            response = requests.post(
                webhook_url,
                json=test_event,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"回應狀態碼: {response.status_code}")
            print(f"回應內容: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ {event_type} 訊息測試成功！")
            else:
                print(f"❌ {event_type} 訊息測試失敗！")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到本地伺服器")
        print("請確保 webhook_receiver 正在運行：")
        print("  python webhook_receiver/main.py")
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {e}")

def test_health_check():
    """測試健康檢查端點"""
    
    health_url = "http://localhost:8080/health"
    
    try:
        print("測試健康檢查端點...")
        response = requests.get(health_url, timeout=10)
        
        print(f"健康檢查狀態碼: {response.status_code}")
        print(f"健康檢查回應: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 健康檢查通過！")
        else:
            print("❌ 健康檢查失敗！")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到本地伺服器")
    except Exception as e:
        print(f"❌ 健康檢查時發生錯誤: {e}")

if __name__ == "__main__":
    print("=== LINE Webhook 本地測試 ===\n")
    
    # 測試健康檢查
    test_health_check()
    print()
    
    # 測試 Webhook
    test_line_webhook()
