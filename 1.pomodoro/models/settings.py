"""設定データモデル"""
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Settings:
    """ポモドーロタイマー設定"""
    work_duration: int = 25  # 作業時間（分）
    short_break_duration: int = 5  # 短い休憩時間（分）
    long_break_duration: int = 15  # 長い休憩時間（分）
    pomodoros_until_long_break: int = 4  # 長い休憩までのポモドーロ数
    auto_start_breaks: bool = False  # 休憩自動開始
    auto_start_pomodoros: bool = False  # 作業自動開始
    sound_enabled: bool = True  # 通知音
    sound_volume: float = 0.7  # 音量（0.0-1.0）
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """辞書から設定オブジェクトを生成"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
