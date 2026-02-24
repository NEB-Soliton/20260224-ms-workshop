"""統計情報サービス"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from models.session import PomodoroSession
from repositories.session_repository import SessionRepository


class StatisticsService:
    """ポモドーロ統計情報を計算するサービス"""
    
    def __init__(self, session_repo: SessionRepository):
        """
        Args:
            session_repo: セッションリポジトリ
        """
        self.session_repo = session_repo
    
    def get_today_stats(self) -> Dict[str, Any]:
        """今日の統計情報を取得する
        
        Returns:
            統計情報の辞書
        """
        sessions = self.session_repo.get_today()
        return self._calculate_stats(sessions, "今日")
    
    def get_date_stats(self, date: str) -> Dict[str, Any]:
        """指定日の統計情報を取得する
        
        Args:
            date: 日付（YYYY-MM-DD形式）
            
        Returns:
            統計情報の辞書
        """
        sessions = self.session_repo.get_by_date(date)
        return self._calculate_stats(sessions, date)
    
    def get_week_stats(self) -> Dict[str, Any]:
        """今週の統計情報を取得する
        
        Returns:
            統計情報の辞書
        """
        today = datetime.now()
        # 今週の月曜日を計算
        monday = today - timedelta(days=today.weekday())
        start_date = monday.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        sessions = self.session_repo.get_date_range(start_date, end_date)
        return self._calculate_stats(sessions, "今週")
    
    def _calculate_stats(self, sessions: List[PomodoroSession], period: str) -> Dict[str, Any]:
        """セッションリストから統計情報を計算する
        
        Args:
            sessions: セッションのリスト
            period: 期間の説明（表示用）
            
        Returns:
            統計情報の辞書
        """
        # 作業セッションのみをフィルタリング
        work_sessions = [s for s in sessions if s.session_type == "work" and s.completed]
        
        # 完了したポモドーロ数
        completed_pomodoros = len(work_sessions)
        
        # 累計作業時間（分）
        total_work_time = sum(s.duration for s in work_sessions)
        
        # 平均作業時間（分）
        average_duration = total_work_time / completed_pomodoros if completed_pomodoros > 0 else 0
        
        # 休憩セッションの統計
        break_sessions = [s for s in sessions if s.session_type in ["short_break", "long_break"]]
        total_break_time = sum(s.duration for s in break_sessions)
        
        return {
            "period": period,
            "completed_pomodoros": completed_pomodoros,
            "total_work_time_minutes": total_work_time,
            "total_work_time_hours": round(total_work_time / 60, 2),
            "average_duration_minutes": round(average_duration, 1),
            "total_break_time_minutes": total_break_time,
            "total_sessions": len(sessions),
            "work_sessions": len(work_sessions),
            "break_sessions": len(break_sessions)
        }
    
    def get_daily_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """過去N日間の日別統計を取得する
        
        Args:
            days: 取得する日数
            
        Returns:
            日別統計のリスト
        """
        today = datetime.now()
        history = []
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            stats = self.get_date_stats(date)
            stats["date"] = date
            history.append(stats)
        
        return list(reversed(history))
