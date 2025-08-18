#!/usr/bin/env python3
"""
環境變數設定腳本
協助用戶快速設定不同環境的環境變數
"""

import os
import sys
import shutil
from pathlib import Path

def setup_environment():
    """設定環境變數"""
    print("🚀 LINE 文件處理系統 - 環境變數設定")
    print("=" * 50)
    
    # 選擇環境
    print("\n📋 請選擇環境：")
    print("1. 本地開發環境 (local)")
    print("2. 生產環境 (production)")
    print("3. 自訂環境")
    
    choice = input("\n請輸入選項 (1-3): ").strip()
    
    env_name = ""
    if choice == "1":
        env_name = "local"
        source_file = "env.example"
    elif choice == "2":
        env_name = "production"
        source_file = "env.example"
    elif choice == "3":
        env_name = input("請輸入環境名稱: ").strip()
        source_file = "env.example"
    else:
        print("❌ 無效的選項")
        return False
    
    # 檢查來源檔案是否存在
    if not os.path.exists(source_file):
        print(f"❌ 找不到來源檔案: {source_file}")
        return False
    
    # 建立目標檔案名稱
    target_file = f".env.{env_name}"
    
    # 檢查目標檔案是否已存在
    if os.path.exists(target_file):
        overwrite = input(f"⚠️  檔案 {target_file} 已存在，是否覆蓋？(y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ 操作已取消")
            return False
    
    try:
        # 複製檔案
        shutil.copy2(source_file, target_file)
        print(f"✅ 已建立環境變數檔案: {target_file}")
        
        # 提示用戶編輯檔案
        print(f"\n📝 請編輯 {target_file} 檔案，填入您的設定值")
        print("💡 提示：")
        print("   - 請從 LINE Developer Console 取得 Channel Access Token")
        print("   - 請從 GCP Console 取得專案 ID 和 Processor ID")
        print("   - 請確保所有必需的變數都已設定")
        
        # 詢問是否要開啟檔案編輯器
        edit_now = input(f"\n是否現在編輯 {target_file}？(y/N): ").strip().lower()
        if edit_now == 'y':
            open_file_in_editor(target_file)
        
        return True
        
    except Exception as e:
        print(f"❌ 建立環境變數檔案時發生錯誤: {e}")
        return False

def open_file_in_editor(file_path):
    """在預設編輯器中開啟檔案"""
    try:
        if sys.platform.startswith('darwin'):  # macOS
            os.system(f'open {file_path}')
        elif sys.platform.startswith('win'):   # Windows
            os.system(f'start {file_path}')
        else:  # Linux
            os.system(f'xdg-open {file_path}')
        print(f"📂 已在編輯器中開啟: {file_path}")
    except Exception as e:
        print(f"⚠️  無法自動開啟編輯器: {e}")
        print(f"請手動開啟檔案: {file_path}")

def validate_environment():
    """驗證環境變數設定"""
    print("\n🔍 驗證環境變數設定...")
    
    # 檢查環境變數檔案
    env_files = ['.env.local', '.env.production', '.env']
    found_files = []
    
    for env_file in env_files:
        if os.path.exists(env_file):
            found_files.append(env_file)
            print(f"📁 找到檔案: {env_file}")
    
    if not found_files:
        print("❌ 找不到任何環境變數檔案")
        print("請先執行環境設定")
        return False
    
    print(f"✅ 找到環境變數檔案: {', '.join(found_files)}")
    
    # 載入環境變數進行驗證
    try:
        from config.env_manager import env_manager
        
        # 驗證必需的環境變數
        required_vars = [
            'GCP_PROJECT',
            'BUCKET_NAME',
            'LINE_CHANNEL_ACCESS_TOKEN'
        ]
        
        if env_manager.validate_required_vars(required_vars):
            print("✅ 所有必需的環境變數都已設定")
            env_manager.print_environment_info()
            return True
        else:
            print("❌ 缺少必需的環境變數")
            return False
            
    except ImportError:
        print("⚠️  無法載入環境管理器，請確保已安裝依賴")
        return False
    except Exception as e:
        print(f"❌ 驗證環境變數時發生錯誤: {e}")
        return False

def main():
    """主函數"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            setup_environment()
        elif command == "validate":
            validate_environment()
        elif command == "help":
            print_help()
        else:
            print(f"❌ 未知的命令: {command}")
            print_help()
    else:
        # 互動式模式
        print("🔧 環境變數管理工具")
        print("1. 設定環境變數")
        print("2. 驗證環境變數")
        print("3. 顯示說明")
        
        choice = input("\n請選擇操作 (1-3): ").strip()
        
        if choice == "1":
            setup_environment()
        elif choice == "2":
            validate_environment()
        elif choice == "3":
            print_help()
        else:
            print("❌ 無效的選項")

def print_help():
    """顯示說明"""
    print("""
🔧 環境變數管理工具使用說明

用法:
  python scripts/setup_env.py [命令]

命令:
  setup     設定環境變數檔案
  validate  驗證環境變數設定
  help      顯示此說明

範例:
  python scripts/setup_env.py setup
  python scripts/setup_env.py validate

環境變數檔案:
  .env.local       本地開發環境
  .env.production  生產環境
  .env             通用設定

注意事項:
  - 請勿將包含敏感資訊的 .env 檔案提交到版本控制
  - 定期更換 API 金鑰和 Token
  - 使用強密碼作為 Webhook Secret
    """)

if __name__ == "__main__":
    main()
