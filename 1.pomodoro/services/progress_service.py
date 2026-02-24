"""
進捗サービス - 当日進捗の集計ロジック
"""
from datetime import datetime, timedelta
from typing import List
from models import PomodoroSession, DailyProgress
from repositories import HistoryRepository


class ProgressService:
    """進捗集計サービス"""
    
    def __init__(self, history_repo: HistoryRepository):
        """
        初期化
        
        Args:
            history_repo: 履歴リポジトリ
        """
        self.history_repo = history_repo
    
    def get_today_progress(self) -> DailyProgress:
        """
        当日の進捗を取得する
        
        Returns:
            DailyProgress: 当日の進捗情報
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_progress_by_date(today)
    
    def get_progress_by_date(self, date: str) -> DailyProgress:
        """
        指定日付の進捗を取得する
        
        Args:
            date: 日付（YYYY-MM-DD形式）
            
        Returns:
            DailyProgress: 指定日の進捗情報
        """
        sessions = self.history_repo.get_by_date(date)
        
        # 完了セッション数（作業セッションのみカウント）
        completed_sessions = sum(1 for s in sessions if s.completed and s.session_type == "work")
        
        # 総作業時間（分）
        total_work_time = sum(s.duration for s in sessions if s.session_type == "work" and s.completed)
        
        # 総休憩時間（分）
        total_break_time = sum(s.duration for s in sessions if s.session_type == "break" and s.completed)
        
        return DailyProgress(
            date=date,
            completed_sessions=completed_sessions,
            total_work_time=total_work_time,
            total_break_time=total_break_time
        )
    
    def get_weekly_summary(self) -> dict:
        """
        今週のサマリーを取得する
        
        Returns:
            dict: 今週の統計情報
        """
        # 今日から7日分の進捗を取得
        today = datetime.now().date()
        
        weekly_data = []
        total_sessions = 0
        total_time = 0
        
        for i in range(7):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            progress = self.get_progress_by_date(date)
            weekly_data.append(progress.to_dict())
            total_sessions += progress.completed_sessions
            total_time += progress.total_work_time
        
        return {
            "days": weekly_data,
            "total_sessions": total_sessions,
            "total_time": total_time,
            "average_sessions_per_day": round(total_sessions / 7, 1)
        }
