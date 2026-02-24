"""ポモドーロセッションデータモデル"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class PomodoroSession:
    """ポモドーロセッション記録"""
    start_time: str  # ISO形式の開始時刻
    end_time: str  # ISO形式の終了時刻
    duration: int  # 実際の作業時間（分）
    session_type: str  # "work", "short_break", "long_break"
    completed: bool = True  # 完了したかどうか
    note: Optional[str] = None  # メモ
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PomodoroSession':
        """辞書からセッションオブジェクトを生成"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    @property
    def date(self) -> str:
        """セッションの日付を取得（YYYY-MM-DD形式）"""
        dt = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
