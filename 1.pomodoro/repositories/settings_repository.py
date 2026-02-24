"""設定リポジトリ（JSON永続化）"""
import json
import os
from typing import Optional
from models.settings import Settings


class SettingsRepository:
    """設定をJSONファイルで管理するリポジトリ"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: データ保存ディレクトリ
        """
        self.data_dir = data_dir
        self.settings_file = os.path.join(data_dir, "settings.json")
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(data_dir, exist_ok=True)
    
    def load(self) -> Settings:
        """設定を読み込む
        
        Returns:
            設定オブジェクト（ファイルが存在しない場合はデフォルト設定）
        """
        if not os.path.exists(self.settings_file):
            return Settings()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Settings.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"設定ファイルの読み込みに失敗しました: {e}")
            return Settings()
    
    def save(self, settings: Settings) -> bool:
        """設定を保存する
        
        Args:
            settings: 保存する設定オブジェクト
            
        Returns:
            保存が成功したかどうか
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"設定ファイルの保存に失敗しました: {e}")
            return False
    
    def update(self, **kwargs) -> Settings:
        """設定を部分的に更新する
        
        Args:
            **kwargs: 更新する設定項目
            
        Returns:
            更新後の設定オブジェクト
        """
        settings = self.load()
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        self.save(settings)
        return settings
    
    def reset(self) -> Settings:
        """設定をデフォルトにリセットする
        
        Returns:
            デフォルト設定オブジェクト
        """
        settings = Settings()
        self.save(settings)
        return settings
