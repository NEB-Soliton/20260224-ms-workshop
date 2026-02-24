"""
データモデル定義
"""
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Settings:
    """ポモドーロタイマーの設定"""
    work_duration: int = 25  # 作業時間（分）
    short_break: int = 5  # 短い休憩時間（分）
    long_break: int = 15  # 長い休憩時間（分）
    theme: str = "light"  # テーマ: light, dark, focus
    sound_enabled: bool = True  # サウンド有効/無効
    
    def to_dict(self):
        """辞書に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """辞書から生成"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PomodoroSession:
    """ポモドーロセッション履歴"""
    id: str  # セッションID（タイムスタンプベース）
    start_time: str  # 開始時刻（ISO 8601形式）
    end_time: str  # 終了時刻（ISO 8601形式）
    duration: int  # 実際の作業時間（分）
    session_type: str  # "work" または "break"
    completed: bool = True  # 完了したかどうか
    notes: Optional[str] = None  # メモ（オプション）
    
    def to_dict(self):
        """辞書に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """辞書から生成"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class DailyProgress:
    """当日の進捗"""
    date: str  # 日付（YYYY-MM-DD形式）
    completed_sessions: int  # 完了セッション数
    total_work_time: int  # 総作業時間（分）
    total_break_time: int  # 総休憩時間（分）
    
    def to_dict(self):
        """辞書に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """辞書から生成"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
