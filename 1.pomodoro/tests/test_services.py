"""Unit tests for service layer."""
import pytest
from datetime import date, datetime, timezone, timedelta
from models import db, User, PomodoroSession, Badge
from services import GamificationEngine, PomodoroService


class TestGamificationEngine:
    """Test cases for GamificationEngine."""
    
    def test_calculate_xp_no_streak(self):
        """Test XP calculation with no streak bonus."""
        xp = GamificationEngine.calculate_xp(100, 0)
        assert xp == 100
        
        xp = GamificationEngine.calculate_xp(100, 1)
        assert xp == 100
        
        xp = GamificationEngine.calculate_xp(100, 2)
        assert xp == 100
    
    def test_calculate_xp_with_3day_streak(self):
        """Test XP calculation with 3-day streak bonus."""
        xp = GamificationEngine.calculate_xp(100, 3)
        assert xp == 150  # 100 + 50 bonus
        
        xp = GamificationEngine.calculate_xp(100, 4)
        assert xp == 150
        
        xp = GamificationEngine.calculate_xp(100, 6)
        assert xp == 150
    
    def test_calculate_xp_with_7day_streak(self):
        """Test XP calculation with 7-day streak bonus."""
        xp = GamificationEngine.calculate_xp(100, 7)
        assert xp == 200  # 100 + 100 bonus
        
        xp = GamificationEngine.calculate_xp(100, 10)
        assert xp == 200
        
        xp = GamificationEngine.calculate_xp(100, 30)
        assert xp == 200
    
    def test_calculate_level(self):
        """Test level calculation based on XP."""
        # Level 1: 0-199 XP
        assert GamificationEngine.calculate_level(0) == 1
        assert GamificationEngine.calculate_level(100) == 1
        assert GamificationEngine.calculate_level(199) == 1
        
        # Level 2: 200-599 XP (200 + 400)
        assert GamificationEngine.calculate_level(200) == 2
        assert GamificationEngine.calculate_level(400) == 2
        assert GamificationEngine.calculate_level(599) == 2
        
        # Level 3: 600-1199 XP (200 + 400 + 600)
        assert GamificationEngine.calculate_level(600) == 3
        assert GamificationEngine.calculate_level(1000) == 3
        assert GamificationEngine.calculate_level(1199) == 3
        
        # Level 4: 1200-2199 XP (200 + 400 + 600 + 800)
        assert GamificationEngine.calculate_level(1200) == 4
    
    def test_update_streak_first_pomodoro(self, app, test_user):
        """Test streak update for first pomodoro."""
        with app.app_context():
            user = db.session.get(User, test_user)
            assert user.streak_days == 0
            assert user.last_pomodoro_date is None
            
            GamificationEngine.update_streak(user)
            
            assert user.streak_days == 1
            assert user.last_pomodoro_date == date.today()
    
    def test_update_streak_same_day(self, app, test_user):
        """Test streak doesn't change on same day."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.streak_days = 5
            user.last_pomodoro_date = date.today()
            db.session.commit()
            
            GamificationEngine.update_streak(user)
            
            assert user.streak_days == 5
            assert user.last_pomodoro_date == date.today()
    
    def test_update_streak_consecutive_day(self, app, test_user):
        """Test streak increases on consecutive day."""
        with app.app_context():
            user = db.session.get(User, test_user)
            yesterday = date.today() - timedelta(days=1)
            user.streak_days = 5
            user.last_pomodoro_date = yesterday
            db.session.commit()
            
            GamificationEngine.update_streak(user)
            
            assert user.streak_days == 6
            assert user.last_pomodoro_date == date.today()
    
    def test_update_streak_broken(self, app, test_user):
        """Test streak resets when broken."""
        with app.app_context():
            user = db.session.get(User, test_user)
            three_days_ago = date.today() - timedelta(days=3)
            user.streak_days = 10
            user.last_pomodoro_date = three_days_ago
            db.session.commit()
            
            GamificationEngine.update_streak(user)
            
            assert user.streak_days == 1
            assert user.last_pomodoro_date == date.today()
    
    def test_award_badges_first_pomodoro(self, app, test_user):
        """Test first pomodoro badge award."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.total_pomodoros = 1
            
            badges = GamificationEngine.award_badges(user)
            db.session.commit()
            
            assert len(badges) == 1
            assert badges[0]['name'] == 'First Pomodoro'
            
            # Verify badge was saved
            saved_badge = Badge.query.filter_by(
                user_id=test_user,
                name='First Pomodoro'
            ).first()
            assert saved_badge is not None
    
    def test_award_badges_no_duplicate(self, app, test_user):
        """Test that badges are not awarded twice."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.total_pomodoros = 1
            
            # Award first time
            badges1 = GamificationEngine.award_badges(user)
            db.session.commit()
            assert len(badges1) == 1
            
            # Try to award again
            badges2 = GamificationEngine.award_badges(user)
            db.session.commit()
            assert len(badges2) == 0
    
    def test_award_badges_dedicated(self, app, test_user):
        """Test 10 pomodoros badge award."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.total_pomodoros = 10
            
            badges = GamificationEngine.award_badges(user)
            db.session.commit()
            
            assert any(b['name'] == 'Dedicated' for b in badges)
    
    def test_award_badges_master_of_focus(self, app, test_user):
        """Test 50 pomodoros badge award."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.total_pomodoros = 50
            
            badges = GamificationEngine.award_badges(user)
            db.session.commit()
            
            assert any(b['name'] == 'Master of Focus' for b in badges)
    
    def test_award_badges_week_warrior(self, app, test_user):
        """Test 7-day streak badge award."""
        with app.app_context():
            user = db.session.get(User, test_user)
            user.streak_days = 7
            
            badges = GamificationEngine.award_badges(user)
            db.session.commit()
            
            assert any(b['name'] == 'Week Warrior' for b in badges)


class TestPomodoroService:
    """Test cases for PomodoroService."""
    
    def test_start_session_success(self, app, test_user):
        """Test starting a new session."""
        with app.app_context():
            session = PomodoroService.start_session(test_user, 25)
            
            assert session.id is not None
            assert session.user_id == test_user
            assert session.duration == 25
            assert session.completed is False
    
    def test_start_session_invalid_user(self, app):
        """Test starting session with invalid user."""
        with app.app_context():
            with pytest.raises(ValueError, match="User with id 999 not found"):
                PomodoroService.start_session(999, 25)
    
    def test_complete_session_success(self, app, test_user):
        """Test completing a session successfully."""
        with app.app_context():
            # Start a session
            session = PomodoroService.start_session(test_user, 25)
            session_id = session.id
            
            # Complete the session
            result = PomodoroService.complete_session(session_id)
            
            assert result['session'].completed is True
            assert result['xp_earned'] == 100  # Base XP, no streak
            assert result['new_level'] == 1
            assert len(result['badges_awarded']) == 1  # First Pomodoro badge
            
            # Verify user stats updated
            user = db.session.get(User, test_user)
            assert user.total_pomodoros == 1
            assert user.total_work_time == 25
            assert user.xp == 100
            assert user.streak_days == 1
    
    def test_complete_session_invalid_session(self, app):
        """Test completing invalid session."""
        with app.app_context():
            with pytest.raises(ValueError, match="Session with id 999 not found"):
                PomodoroService.complete_session(999)
    
    def test_complete_session_already_completed(self, app, test_user):
        """Test completing an already completed session."""
        with app.app_context():
            # Start and complete a session
            session = PomodoroService.start_session(test_user, 25)
            session_id = session.id
            PomodoroService.complete_session(session_id)
            
            # Try to complete again
            with pytest.raises(ValueError, match="Session .* is already completed"):
                PomodoroService.complete_session(session_id)
    
    def test_complete_multiple_sessions_with_streak(self, app, test_user):
        """Test completing multiple sessions builds streak and XP."""
        with app.app_context():
            user = db.session.get(User, test_user)
            
            # Set user to have completed yesterday
            yesterday = date.today() - timedelta(days=1)
            user.last_pomodoro_date = yesterday
            user.streak_days = 2
            db.session.commit()
            
            # Complete a session today
            session = PomodoroService.start_session(test_user, 25)
            result = PomodoroService.complete_session(session.id)
            
            # Should have 3-day streak now
            user = db.session.get(User, test_user)
            assert user.streak_days == 3
            assert result['xp_earned'] == 150  # 100 + 50 bonus
    
    def test_get_user_stats_success(self, app, test_user):
        """Test getting user statistics."""
        with app.app_context():
            # Create some data
            user = db.session.get(User, test_user)
            user.level = 2
            user.xp = 300
            user.total_pomodoros = 5
            user.total_work_time = 125
            user.streak_days = 3
            
            session = PomodoroSession(user_id=test_user, duration=25, completed=True)
            badge = Badge(user_id=test_user, name='Test', description='Test')
            db.session.add_all([session, badge])
            db.session.commit()
            
            # Get stats
            stats = PomodoroService.get_user_stats(test_user)
            
            assert stats['username'] == 'testuser'
            assert stats['level'] == 2
            assert stats['xp'] == 300
            assert stats['total_pomodoros'] == 5
            assert stats['total_work_time'] == 125
            assert stats['streak_days'] == 3
            assert stats['completed_sessions'] == 1
            assert stats['badges_count'] == 1
    
    def test_get_user_stats_invalid_user(self, app):
        """Test getting stats for invalid user."""
        with app.app_context():
            with pytest.raises(ValueError, match="User with id 999 not found"):
                PomodoroService.get_user_stats(999)
