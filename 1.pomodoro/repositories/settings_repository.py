"""
設定リポジトリ - JSON ファイルベース
"""
import json
import os
from typing import Optional
from models import Settings


class SettingsRepository:
    """設定の永続化を管理するリポジトリ"""
    
    def __init__(self, file_path: str = "data/settings.json"):
        """
        初期化
        
        Args:
            file_path: 設定ファイルのパス
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """設定ファイルが存在することを確認、なければデフォルト設定で作成"""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            default_settings = Settings()
            self.save(default_settings)
    
    def load(self) -> Settings:
        """
        設定を読み込む
        
        Returns:
            Settings: 設定オブジェクト
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Settings.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            # ファイルが存在しないか、無効なJSONの場合はデフォルト設定を返す
            return Settings()
    
    def save(self, settings: Settings) -> bool:
        """
        設定を保存する
        
        Args:
            settings: 保存する設定オブジェクト
            
        Returns:
            bool: 保存に成功したかどうか
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"設定の保存に失敗しました: {e}")
            return False
    
    def update(self, **kwargs) -> Settings:
        """
        設定を部分的に更新する
        
        Args:
            **kwargs: 更新する設定項目
            
        Returns:
            Settings: 更新後の設定オブジェクト
        """
        settings = self.load()
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        self.save(settings)
        return settings
