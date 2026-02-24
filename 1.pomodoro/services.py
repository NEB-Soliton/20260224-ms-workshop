"""Service layer for Pomodoro Timer application."""
from datetime import date, datetime, timezone
from models import db, User, PomodoroSession, Badge


class GamificationEngine:
    """
    Handles XP calculation, level-up logic, streak bonuses, and badge awards.
    
    XP System:
    - Base XP per pomodoro: 100 XP
    - Level-up formula: level × 200 XP
    - Streak bonuses: 3 days (+50 XP), 7 days (+100 XP)
    """
    
    BASE_XP = 100
    XP_PER_LEVEL = 200
    STREAK_3_BONUS = 50
    STREAK_7_BONUS = 100
    
    @staticmethod
    def calculate_xp(base_xp, streak_days):
        """Calculate total XP including streak bonuses."""
        bonus = 0
        if streak_days >= 7:
            bonus = GamificationEngine.STREAK_7_BONUS
        elif streak_days >= 3:
            bonus = GamificationEngine.STREAK_3_BONUS
        return base_xp + bonus
    
    @staticmethod
    def calculate_level(total_xp):
        """Calculate level based on total XP."""
        level = 1
        xp_needed = GamificationEngine.XP_PER_LEVEL
        
        while total_xp >= xp_needed:
            total_xp -= xp_needed
            level += 1
            xp_needed = level * GamificationEngine.XP_PER_LEVEL
        
        return level
    
    @staticmethod
    def update_streak(user):
        """Update user's streak based on last pomodoro date."""
        today = date.today()
        
        if user.last_pomodoro_date is None:
            user.streak_days = 1
        elif user.last_pomodoro_date == today:
            # Same day, don't change streak
            pass
        elif (today - user.last_pomodoro_date).days == 1:
            # Consecutive day
            user.streak_days += 1
        else:
            # Streak broken
            user.streak_days = 1
        
        user.last_pomodoro_date = today
    
    @staticmethod
    def award_badges(user):
        """Check and award badges based on user achievements."""
        badges_to_award = []
        
        # First Pomodoro badge
        if user.total_pomodoros == 1:
            if not Badge.query.filter_by(user_id=user.id, name='First Pomodoro').first():
                badges_to_award.append({
                    'name': 'First Pomodoro',
                    'description': 'Completed your first pomodoro session!'
                })
        
        # 10 Pomodoros badge
        if user.total_pomodoros >= 10:
            if not Badge.query.filter_by(user_id=user.id, name='Dedicated').first():
                badges_to_award.append({
                    'name': 'Dedicated',
                    'description': 'Completed 10 pomodoro sessions!'
                })
        
        # 50 Pomodoros badge
        if user.total_pomodoros >= 50:
            if not Badge.query.filter_by(user_id=user.id, name='Master of Focus').first():
                badges_to_award.append({
                    'name': 'Master of Focus',
                    'description': 'Completed 50 pomodoro sessions!'
                })
        
        # Streak badges
        if user.streak_days >= 7:
            if not Badge.query.filter_by(user_id=user.id, name='Week Warrior').first():
                badges_to_award.append({
                    'name': 'Week Warrior',
                    'description': 'Maintained a 7-day streak!'
                })
        
        # Create badge records
        for badge_data in badges_to_award:
            badge = Badge(
                user_id=user.id,
                name=badge_data['name'],
                description=badge_data['description']
            )
            db.session.add(badge)
        
        return badges_to_award


class PomodoroService:
    """Service for managing pomodoro sessions."""
    
    @staticmethod
    def start_session(user_id, duration):
        """Start a new pomodoro session."""
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        session = PomodoroSession(
            user_id=user_id,
            duration=duration,
            completed=False
        )
        db.session.add(session)
        db.session.commit()
        
        return session
    
    @staticmethod
    def complete_session(session_id):
        """Complete a pomodoro session and update user stats."""
        session = db.session.get(PomodoroSession, session_id)
        if not session:
            raise ValueError(f"Session with id {session_id} not found")
        
        if session.completed:
            raise ValueError(f"Session {session_id} is already completed")
        
        user = session.user
        
        # Update streak
        GamificationEngine.update_streak(user)
        
        # Calculate XP
        xp_earned = GamificationEngine.calculate_xp(
            GamificationEngine.BASE_XP,
            user.streak_days
        )
        
        # Update session
        session.completed = True
        session.completed_at = datetime.now(timezone.utc)
        session.xp_earned = xp_earned
        
        # Update user stats
        user.total_pomodoros += 1
        user.total_work_time += session.duration
        user.xp += xp_earned
        user.level = GamificationEngine.calculate_level(user.xp)
        
        # Award badges
        badges_awarded = GamificationEngine.award_badges(user)
        
        db.session.commit()
        
        return {
            'session': session,
            'xp_earned': xp_earned,
            'badges_awarded': badges_awarded,
            'new_level': user.level
        }
    
    @staticmethod
    def get_user_stats(user_id):
        """Get user statistics."""
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        completed_sessions = PomodoroSession.query.filter_by(
            user_id=user_id,
            completed=True
        ).count()
        
        badges = Badge.query.filter_by(user_id=user_id).all()
        
        return {
            'username': user.username,
            'level': user.level,
            'xp': user.xp,
            'total_pomodoros': user.total_pomodoros,
            'total_work_time': user.total_work_time,
            'streak_days': user.streak_days,
            'completed_sessions': completed_sessions,
            'badges_count': len(badges)
        }
