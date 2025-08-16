import os
import requests
import json
import logging
from datetime import datetime
from flask import Flask, request, abort
from dotenv import load_dotenv
from pathlib import Path
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError

# 取得專案根目錄並載入環境變數
project_root = Path(__file__).parent.parent
env_file = project_root / '.env.local'

print(f"專案根目錄: {project_root}")
print(f"環境變數檔案: {env_file}")
print(f"檔案是否存在: {env_file.exists()}")

# 載入環境變數
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ 成功載入環境變數檔案: {env_file}")
else:
    print(f"❌ 環境變數檔案不存在: {env_file}")
    # 嘗試載入當前目錄的 .env.local
    current_env = Path.cwd() / '.env.local'
    if current_env.exists():
        load_dotenv(current_env)
        print(f"✅ 成功載入當前目錄環境變數檔案: {current_env}")
    else:
        print(f"❌ 當前目錄環境變數檔案也不存在: {current_env}")

app = Flask(__name__)

# --- 從環境變數讀取設定 ---
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ID = os.getenv('LINE_CHANNEL_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# 用戶和群組 ID 設定
LINE_USER_ID_CURRENT = os.getenv('LINE_USER_ID_CURRENT')
LINE_GROUP_ID_CURRENT = os.getenv('LINE_GROUP_ID_CURRENT')
LINE_USER_ID_SAM = os.getenv('LINE_USER_ID_SAM')
LINE_GROUP_ID_TEMP = os.getenv('LINE_GROUP_ID_TEMP')
LINE_GROUP_ID_PATROL = os.getenv('LINE_GROUP_ID_PATROL')

# 檢查環境變數是否正確載入
if not LINE_CHANNEL_ACCESS_TOKEN:
    print("⚠️  警告: LINE_CHANNEL_ACCESS_TOKEN 未設定")
else:
    print(f"✅ LINE Token 已載入: {LINE_CHANNEL_ACCESS_TOKEN[:20]}...")

if not LINE_CHANNEL_SECRET:
    print("⚠️  警告: LINE_CHANNEL_SECRET 未設定")
else:
    print(f"✅ LINE Secret 已載入: {LINE_CHANNEL_SECRET[:10]}...")

# 檢查用戶和群組 ID
if LINE_USER_ID_CURRENT:
    print(f"✅ 當前用戶 ID: {LINE_USER_ID_CURRENT}")
if LINE_GROUP_ID_CURRENT:
    print(f"✅ 當前群組 ID: {LINE_GROUP_ID_CURRENT}")
if LINE_USER_ID_SAM:
    print(f"✅ SAM 用戶 ID: {LINE_USER_ID_SAM}")
if LINE_GROUP_ID_TEMP:
    print(f"✅ TEMP 群組 ID: {LINE_GROUP_ID_TEMP}")
if LINE_GROUP_ID_PATROL:
    print(f"✅ PATROL 群組 ID: {LINE_GROUP_ID_PATROL}")

def line_webhook_handler(request):
    """處理 LINE Webhook 請求 (適用於 Flask 和 Cloud Function)"""
    try:
        # 取得原始請求資料
        if hasattr(request, 'get_json'):
            # Flask 請求
            data = request.get_json()
        else:
            # Cloud Function 請求
            data = request.get_json()
        
        if not data:
            print("收到空的請求資料")
            return ('OK', 200)
        
        print(f"收到 LINE Webhook: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 處理每個事件
        for event in data.get('events', []):
            event_type = event.get('type')
            print(f"處理事件類型: {event_type}")
            
            if event_type == 'message':
                handle_message_event(event)
            elif event_type == 'follow':
                handle_follow_event(event)
            elif event_type == 'unfollow':
                handle_unfollow_event(event)
            else:
                print(f"未處理的事件類型: {event_type}")
        
        return ('OK', 200)
        
    except Exception as e:
        print(f"處理 Webhook 時發生錯誤: {e}")
        return ('Error', 500)

@app.route("/", methods=['POST'])
def line_webhook_flask():
    """接收 LINE Webhook 的主要端點 (Flask 路由)"""
    return line_webhook_handler(request)

def handle_message_event(event):
    """處理訊息事件"""
    message = event.get('message', {})
    message_type = message.get('type')
    
    print(f"處理訊息類型: {message_type}")
    
    if message_type == 'text':
        handle_text_message(event)
    elif message_type == 'file':
        handle_file_message(event)
    elif message_type == 'image':
        handle_image_message(event)
    else:
        print(f"未處理的訊息類型: {message_type}")

def handle_text_message(event):
    """處理文字訊息"""
    text = event['message']['text']
    reply_token = event.get('replyToken')
    user_id = event['source'].get('userId')
    
    print(f"收到文字訊息: {text}")
    
    # 簡單的回覆邏輯
    reply_message = f"收到您的訊息: {text}"
    reply_to_user(reply_token, reply_message, user_id)

def handle_file_message(event):
    """處理檔案訊息"""
    message_id = event['message']['id']
    file_name = event['message']['fileName']
    file_size = event['message']['fileSize']
    reply_token = event.get('replyToken')
    user_id = event['source'].get('userId')
    
    print(f"收到檔案: {file_name} (大小: {file_size} bytes)")
    
    # 階段 1：立即回覆（使用 reply token）
    immediate_reply = f"📥 開始下載檔案：{file_name}"
    reply_to_user(reply_token, immediate_reply, user_id)
    
    try:
        # 階段 2：下載檔案
        print(f"開始下載檔案 {message_id}...")
        downloaded_file = download_line_file(message_id, file_name)
        
        # 階段 3：下載完成後用 push message 回覆結果
        if downloaded_file:
            result_message = f"✅ 檔案下載成功！\n📁 檔案名稱: {file_name}\n💾 檔案大小: {file_size} bytes\n📂 儲存位置: {downloaded_file}"
        else:
            result_message = f"❌ 檔案下載失敗: {file_name}\n請檢查檔案是否仍在 LINE 中可用"
            
        # 使用 push message 發送結果（因為 reply token 可能已過期）
        push_message_to_user(user_id, result_message)
            
    except Exception as e:
        print(f"處理檔案時發生錯誤: {e}")
        error_message = f"❌ 處理檔案時發生錯誤: {file_name}\n錯誤: {str(e)}"
        push_message_to_user(user_id, error_message)

def download_line_image(message_id):
    """從 LINE 下載圖片"""
    try:
        # 使用 LINE Bot SDK 取得圖片內容（參考網頁教學）
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        
        print(f"正在下載圖片: {message_id}")
        print(f"使用 LINE Bot SDK...")
        
        # 使用 get_message_content 方法取得訊息內容
        message_content = line_bot_api.get_message_content(message_id)
        
        print(f"成功取得圖片內容")
        print(f"內容類型: {message_content.content_type}")
        print(f"內容大小: {len(message_content.content)} bytes")
        
        # 建立桌面下載目錄
        desktop_path = os.path.expanduser("~/Desktop")
        download_dir = os.path.join(desktop_path, "LINE_Downloads")
        os.makedirs(download_dir, exist_ok=True)
        
        # 根據內容類型判斷圖片格式
        content_type = message_content.content_type
        if 'jpeg' in content_type or 'jpg' in content_type:
            extension = '.jpg'
        elif 'png' in content_type:
            extension = '.png'
        elif 'gif' in content_type:
            extension = '.gif'
        else:
            extension = '.jpg'  # 預設為 jpg
        
        # 儲存圖片（參考網頁教學的寫法）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINE_Image_{timestamp}{extension}"
        file_path = os.path.join(download_dir, filename)
        
        # 使用二進位模式寫入檔案
        with open(file_path, 'wb') as f:
            f.write(message_content.content)  # 以二進位的方式寫入檔案
        
        # 檢查檔案是否成功寫入
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            print(f"✅ 圖片已儲存: {file_path}")
            print(f"圖片大小: {os.path.getsize(file_path)} bytes")
            return file_path
        else:
            print(f"❌ 圖片寫入失敗或檔案為空")
            return None
        
    except LineBotApiError as e:
        print(f"❌ LINE Bot API 錯誤: {e}")
        print(f"錯誤狀態碼: {e.status_code}")
        print(f"錯誤訊息: {e.message}")
        return None
    except Exception as e:
        print(f"❌ 儲存圖片失敗: {e}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")
        return None

def download_line_file(message_id, file_name):
    """從 LINE 下載檔案"""
    try:
        # 先嘗試取得檔案資訊
        print(f"🔍 先取得檔案資訊...")
        info_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content/header"
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        info_response = requests.get(info_url, headers=headers, timeout=30)
        print(f"檔案資訊回應: {info_response.status_code}")
        if info_response.status_code == 200:
            print(f"檔案資訊: {info_response.text}")
        
        # 方法 1: 嘗試使用標準的 content API
        content_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
        
        print(f"正在下載檔案: {file_name}")
        print(f"下載 URL: {content_url}")
        print(f"使用 Token: {LINE_CHANNEL_ACCESS_TOKEN[:20]}...")
        
        # 先嘗試不帶 stream 的請求
        response = requests.get(content_url, headers=headers, timeout=60)
        
        print(f"回應狀態碼: {response.status_code}")
        print(f"回應標頭: {dict(response.headers)}")
        
        if response.status_code == 200:
            # 建立桌面下載目錄
            desktop_path = os.path.expanduser("~/Desktop")
            download_dir = os.path.join(desktop_path, "LINE_Downloads")
            os.makedirs(download_dir, exist_ok=True)
            
            # 儲存檔案
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{timestamp}_{file_name}"
            file_path = os.path.join(download_dir, safe_filename)
            
            # 使用二進位模式寫入檔案
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # 檢查檔案是否成功寫入
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"✅ 檔案已儲存: {file_path}")
                print(f"檔案大小: {os.path.getsize(file_path)} bytes")
                return file_path
            else:
                print(f"❌ 檔案寫入失敗或檔案為空")
                return None
        else:
            print(f"❌ 標準 API 下載失敗: {response.status_code}")
            print(f"錯誤內容: {response.text}")
            
            # 方法 2: 嘗試使用不同的 API 端點
            print("🔄 嘗試使用備用 API 端點...")
            alt_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content/stream"
            alt_response = requests.get(alt_url, headers=headers, timeout=60)
            
            print(f"備用 API 回應狀態碼: {alt_response.status_code}")
            
            if alt_response.status_code == 200:
                # 儲存檔案
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_filename = f"{timestamp}_{file_name}"
                file_path = os.path.join(download_dir, safe_filename)
                
                with open(file_path, 'wb') as f:
                    f.write(alt_response.content)
                
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    print(f"✅ 使用備用 API 檔案已儲存: {file_path}")
                    print(f"檔案大小: {os.path.getsize(file_path)} bytes")
                    return file_path
            
            # 方法 3: 嘗試使用不同的請求方式
            print("🔄 嘗試使用 POST 請求...")
            post_response = requests.post(content_url, headers=headers, timeout=60)
            
            print(f"POST 請求回應狀態碼: {post_response.status_code}")
            
            if post_response.status_code == 200:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_filename = f"{timestamp}_{file_name}"
                file_path = os.path.join(download_dir, safe_filename)
                
                with open(file_path, 'wb') as f:
                    f.write(post_response.content)
                
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    print(f"✅ 使用 POST 請求檔案已儲存: {file_path}")
                    print(f"檔案大小: {os.path.getsize(file_path)} bytes")
                    return file_path
            
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 下載檔案失敗: {e}")
        return None
    except Exception as e:
        print(f"❌ 儲存檔案失敗: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return None

def handle_image_message(event):
    """處理圖片訊息"""
    message_id = event['message']['id']
    reply_token = event.get('replyToken')
    user_id = event['source'].get('userId')
    
    print(f"收到圖片訊息，ID: {message_id}")
    
    # 階段 1：立即回覆（使用 reply token）
    immediate_reply = "📸 開始下載圖片..."
    reply_to_user(reply_token, immediate_reply, user_id)
    
    try:
        # 階段 2：下載圖片
        print(f"開始下載圖片 {message_id}...")
        downloaded_image = download_line_image(message_id)
        
        # 階段 3：下載完成後用 push message 回覆結果
        if downloaded_image:
            result_message = f"✅ 圖片下載成功！\n📁 檔案名稱: {os.path.basename(downloaded_image)}\n📂 儲存位置: {downloaded_image}"
        else:
            result_message = f"❌ 圖片下載失敗\n請檢查圖片是否仍在 LINE 中可用"
            
        # 使用 push message 發送結果（因為 reply token 可能已過期）
        push_message_to_user(user_id, result_message)
            
    except Exception as e:
        print(f"處理圖片時發生錯誤: {e}")
        error_message = f"❌ 處理圖片時發生錯誤\n錯誤: {str(e)}"
        push_message_to_user(user_id, error_message)

def handle_follow_event(event):
    """處理加好友事件"""
    user_id = event['source']['userId']
    reply_token = event.get('replyToken')
    
    print(f"新用戶加好友: {user_id}")
    
    welcome_message = "歡迎使用 LINE 文件處理系統！\n請上傳文件或圖片，我會協助您處理。"
    reply_to_user(reply_token, welcome_message, user_id)

def handle_unfollow_event(event):
    """處理取消好友事件"""
    user_id = event['source']['userId']
    print(f"用戶取消好友: {user_id}")

def reply_to_user(reply_token, message, user_id=None, group_id=None):
    """回覆 LINE 用戶訊息"""
    try:
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # 優先使用 reply token（如果有效）
        if reply_token:
            url = "https://api.line.me/v2/bot/message/reply"
            data = {
                'replyToken': reply_token,
                'messages': [{'type': 'text', 'text': message}]
            }
        # 如果 reply token 無效，使用 push message
        elif user_id:
            url = "https://api.line.me/v2/bot/message/push"
            data = {
                'to': user_id,
                'messages': [{'type': 'text', 'text': message}]
            }
        else:
            print("❌ 無法發送訊息：沒有有效的 reply token 或 user_id")
            return
        
        print(f"發送訊息請求: {json.dumps(data, ensure_ascii=False)}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 已發送訊息: {message}")
        else:
            print(f"❌ 發送失敗: {response.status_code} - {response.text}")
            # 如果是 reply token 無效，嘗試使用 push message
            if response.status_code == 400 and "Invalid reply token" in response.text and user_id:
                print("🔄 嘗試使用 push message...")
                push_message_to_user(user_id, message)
        
    except Exception as e:
        print(f"發送訊息失敗: {e}")

def push_message_to_user(user_id, message):
    """使用 push message 發送訊息給用戶"""
    try:
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        data = {
            'to': user_id,
            'messages': [{'type': 'text', 'text': message}]
        }
        
        print(f"發送 push message: {json.dumps(data, ensure_ascii=False)}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 已使用 push message 發送: {message}")
        else:
            print(f"❌ push message 失敗: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"push message 發送失敗: {e}")

def health_check_handler():
    """健康檢查處理函數"""
    return {'status': 'healthy', 'service': 'line-webhook-receiver'}, 200

@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查端點 (Flask 路由)"""
    return health_check_handler()

# Cloud Function 入口點
def line_webhook(request):
    """Cloud Function 入口點"""
    # 處理 GET 請求 (健康檢查)
    if request.method == 'GET':
        return health_check_handler()
    # 處理 POST 請求 (LINE Webhook)
    elif request.method == 'POST':
        return line_webhook_handler(request)
    else:
        return ('Method not allowed', 405)

if __name__ == "__main__":
    # 本地開發模式
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"啟動本地測試伺服器於 port {port}")
    print(f"Debug 模式: {debug}")
    print(f"LINE Token: {LINE_CHANNEL_ACCESS_TOKEN[:20] if LINE_CHANNEL_ACCESS_TOKEN else '未設定'}...")
    print(f"LINE Channel ID: {LINE_CHANNEL_ID or '未設定'}")
    print(f"Webhook URL: {WEBHOOK_URL or '未設定'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
