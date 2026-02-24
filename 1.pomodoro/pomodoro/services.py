"""
Service layer for business logic
"""
from datetime import datetime, timedelta


class GamificationEngine:
    """
    Gamification engine for Pomodoro timer
    経験値とバッジの管理
    """
    
    XP_PER_COMPLETION = 100
    STREAK_3_BONUS = 50
    STREAK_7_BONUS = 100
    
    def calculate_level(self, xp):
        """
        Calculate level from XP
        Formula: level × 200 XP per level
        """
        if xp <= 0:
            return 1
        
        level = 1
        xp_for_next = 200
        
        while xp >= xp_for_next:
            xp -= xp_for_next
            level += 1
            xp_for_next = level * 200
        
        return level
    
    def calculate_xp_for_level(self, level):
        """Calculate total XP needed to reach a specific level"""
        if level <= 1:
            return 0
        
        total_xp = 0
        for lvl in range(1, level):
            total_xp += lvl * 200
        
        return total_xp
    
    def calculate_rewards(self, sessions):
        """
        Calculate rewards (XP, level, badges) based on sessions
        
        Args:
            sessions: List of session dictionaries with 'completed', 'timestamp' fields
            
        Returns:
            dict with xp, level, badges, streak information
        """
        completed_sessions = [s for s in sessions if s.get('completed', False)]
        
        # Calculate base XP
        base_xp = len(completed_sessions) * self.XP_PER_COMPLETION
        
        # Calculate streak
        streak = self._calculate_streak(completed_sessions)
        
        # Calculate streak bonus
        streak_bonus = 0
        if streak >= 7:
            streak_bonus = self.STREAK_7_BONUS
        elif streak >= 3:
            streak_bonus = self.STREAK_3_BONUS
        
        # Total XP
        total_xp = base_xp + streak_bonus
        
        # Calculate level
        level = self.calculate_level(total_xp)
        
        # Calculate badges
        badges = self._calculate_badges(completed_sessions, streak)
        
        return {
            'xp': total_xp,
            'level': level,
            'streak': streak,
            'streak_bonus': streak_bonus,
            'badges': badges,
            'completed_count': len(completed_sessions)
        }
    
    def _calculate_streak(self, completed_sessions):
        """Calculate current streak of consecutive days"""
        if not completed_sessions:
            return 0
        
        # Sort sessions by timestamp (newest first)
        sorted_sessions = sorted(
            completed_sessions,
            key=lambda s: datetime.fromisoformat(s['timestamp']),
            reverse=True
        )
        
        # Get unique dates
        dates = set()
        for session in sorted_sessions:
            date = datetime.fromisoformat(session['timestamp']).date()
            dates.add(date)
        
        sorted_dates = sorted(dates, reverse=True)
        
        if not sorted_dates:
            return 0
        
        # Check for streak starting from today or yesterday
        today = datetime.utcnow().date()
        streak = 0
        
        # If most recent date is today or yesterday, start counting
        if sorted_dates[0] == today or sorted_dates[0] == today - timedelta(days=1):
            expected_date = sorted_dates[0]
            
            for date in sorted_dates:
                if date == expected_date:
                    streak += 1
                    expected_date = date - timedelta(days=1)
                else:
                    break
        
        return streak
    
    def _calculate_badges(self, completed_sessions, streak):
        """Calculate earned badges"""
        badges = []
        count = len(completed_sessions)
        
        # Streak badges
        if streak >= 3:
            badges.append({'id': 'streak_3', 'name': '3日連続', 'description': '3日連続でポモドーロを完了'})
        if streak >= 7:
            badges.append({'id': 'streak_7', 'name': '1週間連続', 'description': '7日連続でポモドーロを完了'})
        
        # Completion count badges
        if count >= 10:
            badges.append({'id': 'novice', 'name': '初心者', 'description': '10回のポモドーロを完了'})
        if count >= 50:
            badges.append({'id': 'intermediate', 'name': '中級者', 'description': '50回のポモドーロを完了'})
        if count >= 100:
            badges.append({'id': 'expert', 'name': '上級者', 'description': '100回のポモドーロを完了'})
        
        return badges
