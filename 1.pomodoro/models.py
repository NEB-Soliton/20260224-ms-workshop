"""Database models for Pomodoro Timer application."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model for tracking pomodoro statistics and progress."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    total_pomodoros = db.Column(db.Integer, default=0)
    total_work_time = db.Column(db.Integer, default=0)  # in minutes
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    last_pomodoro_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('PomodoroSession', backref='user', lazy=True, cascade='all, delete-orphan')
    badges = db.relationship('Badge', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class PomodoroSession(db.Model):
    """Pomodoro session history model."""
    __tablename__ = 'pomodoro_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    completed = db.Column(db.Boolean, default=False)
    xp_earned = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<PomodoroSession {self.id} - User {self.user_id}>'


class Badge(db.Model):
    """Achievement badges model."""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Badge {self.name} - User {self.user_id}>'
