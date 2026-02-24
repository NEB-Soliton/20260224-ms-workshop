"""Unit tests for database models."""
import pytest
from datetime import date, datetime, timezone
from models import db, User, PomodoroSession, Badge


class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, app):
        """Test creating a new user."""
        with app.app_context():
            user = User(username='testuser')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.total_pomodoros == 0
            assert user.total_work_time == 0
            assert user.level == 1
            assert user.xp == 0
            assert user.streak_days == 0
            assert user.last_pomodoro_date is None
            assert user.created_at is not None
    
    def test_user_unique_username(self, app):
        """Test that username must be unique."""
        with app.app_context():
            user1 = User(username='testuser')
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(username='testuser')
            db.session.add(user2)
            
            with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
                db.session.commit()
    
    def test_user_relationships(self, app):
        """Test user relationships with sessions and badges."""
        with app.app_context():
            user = User(username='testuser')
            db.session.add(user)
            db.session.commit()
            
            # Add a session
            session = PomodoroSession(user_id=user.id, duration=25)
            db.session.add(session)
            
            # Add a badge
            badge = Badge(user_id=user.id, name='Test Badge', description='Test')
            db.session.add(badge)
            
            db.session.commit()
            
            assert len(user.sessions) == 1
            assert len(user.badges) == 1
            assert user.sessions[0].duration == 25
            assert user.badges[0].name == 'Test Badge'
    
    def test_user_cascade_delete(self, app):
        """Test that deleting a user cascades to sessions and badges."""
        with app.app_context():
            user = User(username='testuser')
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Add a session and badge
            session = PomodoroSession(user_id=user.id, duration=25)
            badge = Badge(user_id=user.id, name='Test', description='Test')
            db.session.add_all([session, badge])
            db.session.commit()
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            # Verify cascade
            assert PomodoroSession.query.filter_by(user_id=user_id).count() == 0
            assert Badge.query.filter_by(user_id=user_id).count() == 0


class TestPomodoroSessionModel:
    """Test cases for PomodoroSession model."""
    
    def test_create_session(self, app, test_user):
        """Test creating a new pomodoro session."""
        with app.app_context():
            session = PomodoroSession(user_id=test_user, duration=25)
            db.session.add(session)
            db.session.commit()
            
            assert session.id is not None
            assert session.user_id == test_user
            assert session.duration == 25
            assert session.completed is False
            assert session.xp_earned == 0
            assert session.started_at is not None
            assert session.completed_at is None
    
    def test_complete_session(self, app, test_user):
        """Test completing a pomodoro session."""
        with app.app_context():
            session = PomodoroSession(user_id=test_user, duration=25)
            db.session.add(session)
            db.session.commit()
            
            # Complete the session
            session.completed = True
            session.completed_at = datetime.now(timezone.utc)
            session.xp_earned = 100
            db.session.commit()
            
            assert session.completed is True
            assert session.completed_at is not None
            assert session.xp_earned == 100
    
    def test_session_user_relationship(self, app, test_user):
        """Test session belongs to user."""
        with app.app_context():
            session = PomodoroSession(user_id=test_user, duration=25)
            db.session.add(session)
            db.session.commit()
            
            assert session.user is not None
            assert session.user.id == test_user


class TestBadgeModel:
    """Test cases for Badge model."""
    
    def test_create_badge(self, app, test_user):
        """Test creating a new badge."""
        with app.app_context():
            badge = Badge(
                user_id=test_user,
                name='First Pomodoro',
                description='Completed your first pomodoro!'
            )
            db.session.add(badge)
            db.session.commit()
            
            assert badge.id is not None
            assert badge.user_id == test_user
            assert badge.name == 'First Pomodoro'
            assert badge.description == 'Completed your first pomodoro!'
            assert badge.earned_at is not None
    
    def test_badge_user_relationship(self, app, test_user):
        """Test badge belongs to user."""
        with app.app_context():
            badge = Badge(
                user_id=test_user,
                name='Test Badge',
                description='Test'
            )
            db.session.add(badge)
            db.session.commit()
            
            assert badge.user is not None
            assert badge.user.id == test_user
