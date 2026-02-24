"""セッション履歴リポジトリ（JSON永続化）"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.session import PomodoroSession


class SessionRepository:
    """ポモドーロセッション履歴をJSONファイルで管理するリポジトリ"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: データ保存ディレクトリ
        """
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(data_dir, exist_ok=True)
    
    def load_all(self) -> List[PomodoroSession]:
        """全てのセッション履歴を読み込む
        
        Returns:
            セッションオブジェクトのリスト
        """
        if not os.path.exists(self.sessions_file):
            return []
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [PomodoroSession.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError) as e:
            print(f"セッション履歴ファイルの読み込みに失敗しました: {e}")
            return []
    
    def save_all(self, sessions: List[PomodoroSession]) -> bool:
        """全てのセッション履歴を保存する
        
        Args:
            sessions: 保存するセッションのリスト
            
        Returns:
            保存が成功したかどうか
        """
        try:
            data = [session.to_dict() for session in sessions]
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"セッション履歴ファイルの保存に失敗しました: {e}")
            return False
    
    def add(self, session: PomodoroSession) -> bool:
        """新しいセッションを追加する
        
        Args:
            session: 追加するセッション
            
        Returns:
            追加が成功したかどうか
        """
        sessions = self.load_all()
        sessions.append(session)
        return self.save_all(sessions)
    
    def get_by_date(self, date: str) -> List[PomodoroSession]:
        """指定日のセッションを取得する
        
        Args:
            date: 日付（YYYY-MM-DD形式）
            
        Returns:
            指定日のセッションのリスト
        """
        sessions = self.load_all()
        return [s for s in sessions if s.date == date]
    
    def get_today(self) -> List[PomodoroSession]:
        """今日のセッションを取得する
        
        Returns:
            今日のセッションのリスト
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_by_date(today)
    
    def get_date_range(self, start_date: str, end_date: str) -> List[PomodoroSession]:
        """指定期間のセッションを取得する
        
        Args:
            start_date: 開始日（YYYY-MM-DD形式）
            end_date: 終了日（YYYY-MM-DD形式）
            
        Returns:
            指定期間のセッションのリスト
        """
        sessions = self.load_all()
        return [s for s in sessions if start_date <= s.date <= end_date]
    
    def clear_all(self) -> bool:
        """全てのセッション履歴を削除する
        
        Returns:
            削除が成功したかどうか
        """
        return self.save_all([])
