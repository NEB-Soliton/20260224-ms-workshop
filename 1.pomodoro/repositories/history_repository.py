"""
履歴リポジトリ - JSON ファイルベース
"""
import json
import os
import logging
from typing import List, Optional
from datetime import datetime
from models import PomodoroSession

logger = logging.getLogger(__name__)


class HistoryRepository:
    """履歴の永続化を管理するリポジトリ"""
    
    def __init__(self, file_path: str = "data/history.json"):
        """
        初期化
        
        Args:
            file_path: 履歴ファイルのパス
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """履歴ファイルが存在することを確認、なければ空の配列で作成"""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def load_all(self) -> List[PomodoroSession]:
        """
        すべての履歴を読み込む
        
        Returns:
            List[PomodoroSession]: 履歴のリスト
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [PomodoroSession.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def add(self, session: PomodoroSession) -> bool:
        """
        新しいセッションを追加する
        
        Args:
            session: 追加するセッション
            
        Returns:
            bool: 追加に成功したかどうか
        """
        try:
            sessions = self.load_all()
            sessions.append(session)
            self._save_all(sessions)
            return True
        except Exception as e:
            logger.error(f"セッションの追加に失敗しました: {e}")
            return False
    
    def _save_all(self, sessions: List[PomodoroSession]):
        """
        すべての履歴を保存する（内部用）
        
        Args:
            sessions: 保存するセッションのリスト
        """
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            data = [session.to_dict() for session in sessions]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_by_date(self, date: str) -> List[PomodoroSession]:
        """
        指定日付のセッションを取得する
        
        Args:
            date: 日付（YYYY-MM-DD形式）
            
        Returns:
            List[PomodoroSession]: 該当日のセッションリスト
        """
        sessions = self.load_all()
        result = []
        for session in sessions:
            # start_time から日付を抽出
            session_date = session.start_time.split('T')[0]
            if session_date == date:
                result.append(session)
        return result
    
    def get_recent(self, limit: int = 10) -> List[PomodoroSession]:
        """
        最近のセッションを取得する
        
        Args:
            limit: 取得する件数
            
        Returns:
            List[PomodoroSession]: 最近のセッションリスト
        """
        sessions = self.load_all()
        # 新しい順にソート
        sessions.sort(key=lambda x: x.start_time, reverse=True)
        return sessions[:limit]
