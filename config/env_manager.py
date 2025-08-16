"""
環境變數管理工具
支援本地開發、測試和生產環境的設定管理
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class EnvironmentManager:
    """環境變數管理器"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化環境管理器
        
        Args:
            env_file: 指定的環境變數檔案路徑
        """
        self.env_file = env_file
        self.environment = self._load_environment()
        
        # 設定日誌
        self._setup_logging()
        
    def _load_environment(self) -> str:
        """載入環境變數"""
        # 優先使用指定的環境變數檔案
        if self.env_file and os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            logging.info(f"載入指定的環境變數檔案: {self.env_file}")
            return os.getenv('ENVIRONMENT', 'unknown')
        
        # 根據 ENVIRONMENT 變數載入對應的檔案
        env = os.getenv('ENVIRONMENT', 'local')
        
        # 嘗試載入對應的環境變數檔案
        env_files = [
            f'.env.{env}',
            '.env.local' if env == 'local' else None,
            '.env'
        ]
        
        for env_file in env_files:
            if env_file and os.path.exists(env_file):
                load_dotenv(env_file)
                logging.info(f"載入環境變數檔案: {env_file}")
                break
        
        return env
    
    def _setup_logging(self):
        """設定日誌"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        取得環境變數值
        
        Args:
            key: 環境變數名稱
            default: 預設值
            
        Returns:
            環境變數值
        """
        value = os.getenv(key, default)
        if value is None:
            logging.warning(f"環境變數 {key} 未設定")
        return value
    
    def get_required(self, key: str) -> str:
        """
        取得必需的環境變數值
        
        Args:
            key: 環境變數名稱
            
        Returns:
            環境變數值
            
        Raises:
            ValueError: 如果環境變數未設定
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"必需的環境變數 {key} 未設定")
        return value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        取得布林值環境變數
        
        Args:
            key: 環境變數名稱
            default: 預設值
            
        Returns:
            布林值
        """
        value = self.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        取得整數值環境變數
        
        Args:
            key: 環境變數名稱
            default: 預設值
            
        Returns:
            整數值
        """
        try:
            return int(self.get(key, str(default)))
        except ValueError:
            logging.warning(f"環境變數 {key} 無法轉換為整數，使用預設值 {default}")
            return default
    
    def validate_required_vars(self, required_vars: list) -> bool:
        """
        驗證必需的環境變數
        
        Args:
            required_vars: 必需的環境變數列表
            
        Returns:
            是否所有必需的變數都已設定
        """
        missing_vars = []
        for var in required_vars:
            if not self.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            logging.error(f"缺少必需的環境變數: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def print_environment_info(self):
        """印出環境資訊（不包含敏感資料）"""
        print(f"🌍 環境: {self.environment}")
        print(f"🔧 專案 ID: {self.get('GCP_PROJECT', '未設定')}")
        print(f"📦 原始檔案 Bucket: {self.get('BUCKET_NAME', '未設定')}")
        print(f"📦 處理後檔案 Bucket: {self.get('PROCESSED_BUCKET_NAME', '未設定')}")
        print(f"🐛 Debug 模式: {self.get_bool('DEBUG')}")
        print(f"📝 日誌等級: {self.get('LOG_LEVEL', 'INFO')}")

# 全域環境管理器實例
env_manager = EnvironmentManager()

def get_env(key: str, default: Optional[str] = None) -> str:
    """取得環境變數的便捷函數"""
    return env_manager.get(key, default)

def get_required_env(key: str) -> str:
    """取得必需環境變數的便捷函數"""
    return env_manager.get_required(key)

def get_bool_env(key: str, default: bool = False) -> bool:
    """取得布林值環境變數的便捷函數"""
    return env_manager.get_bool(key, default)

def get_int_env(key: str, default: int = 0) -> int:
    """取得整數值環境變數的便捷函數"""
    return env_manager.get_int(key, default)
