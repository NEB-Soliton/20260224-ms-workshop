"""
Pomodoro Timer App with Gamification Features
- XP/Level System
- Achievement Badges
- Streak Tracking
- Weekly/Monthly Statistics
"""

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pomodoro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    """ユーザー統計情報"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='Player')
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_completion_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sessions = db.relationship('PomodoroSession', backref='user', lazy=True)
    badges = db.relationship('Badge', backref='user', lazy=True)

class PomodoroSession(db.Model):
    """ポモドーロセッション履歴"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration = db.Column(db.Integer, default=25)  # minutes
    completed = db.Column(db.Boolean, default=False)
    xp_earned = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_name = db.Column(db.String(200), nullable=True)

class Badge(db.Model):
    """達成バッジ"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

# Gamification Logic
class GamificationEngine:
    """ゲーミフィケーション処理エンジン"""
    
    # XP設定
    XP_PER_POMODORO = 100
    XP_BONUS_STREAK_3 = 50
    XP_BONUS_STREAK_7 = 100
    
    # レベルアップに必要なXP（レベル×200）
    @staticmethod
    def xp_for_level(level):
        return level * 200
    
    @staticmethod
    def calculate_level(xp):
        """XPからレベルを計算"""
        level = 1
        while xp >= GamificationEngine.xp_for_level(level):
            xp -= GamificationEngine.xp_for_level(level)
            level += 1
        return level
    
    @staticmethod
    def award_xp_for_completion(user, duration=25):
        """ポモドーロ完了時のXP付与"""
        base_xp = GamificationEngine.XP_PER_POMODORO
        
        # ストリークボーナス
        bonus_xp = 0
        if user.current_streak >= 7:
            bonus_xp = GamificationEngine.XP_BONUS_STREAK_7
        elif user.current_streak >= 3:
            bonus_xp = GamificationEngine.XP_BONUS_STREAK_3
        
        total_xp = base_xp + bonus_xp
        
        old_level = user.level
        user.xp += total_xp
        user.level = GamificationEngine.calculate_level(user.xp)
        
        level_up = user.level > old_level
        
        return {
            'xp_earned': total_xp,
            'base_xp': base_xp,
            'bonus_xp': bonus_xp,
            'level_up': level_up,
            'new_level': user.level
        }
    
    @staticmethod
    def update_streak(user):
        """ストリークを更新"""
        today = datetime.utcnow().date()
        
        if user.last_completion_date is None:
            # 初回完了
            user.current_streak = 1
            user.last_completion_date = today
        elif user.last_completion_date == today:
            # 今日既に完了済み
            pass
        elif user.last_completion_date == today - timedelta(days=1):
            # 昨日から継続
            user.current_streak += 1
            user.last_completion_date = today
        else:
            # ストリーク切れ
            user.current_streak = 1
            user.last_completion_date = today
        
        # 最長ストリーク更新
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
    
    @staticmethod
    def check_and_award_badges(user):
        """バッジの確認と付与"""
        new_badges = []
        existing_badge_types = [b.badge_type for b in user.badges]
        
        # 3日連続達成バッジ
        if user.current_streak >= 3 and 'streak_3' not in existing_badge_types:
            badge = Badge(
                user_id=user.id,
                badge_type='streak_3',
                name='🔥 3日連続',
                description='3日連続でポモドーロを完了'
            )
            db.session.add(badge)
            new_badges.append(badge)
        
        # 7日連続達成バッジ
        if user.current_streak >= 7 and 'streak_7' not in existing_badge_types:
            badge = Badge(
                user_id=user.id,
                badge_type='streak_7',
                name='🔥🔥 1週間連続',
                description='7日連続でポモドーロを完了'
            )
            db.session.add(badge)
            new_badges.append(badge)
        
        # 週間10回完了バッジ
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_count = PomodoroSession.query.filter(
            PomodoroSession.user_id == user.id,
            PomodoroSession.completed == True,
            PomodoroSession.completed_at >= week_ago
        ).count()
        
        if week_count >= 10 and 'week_10' not in existing_badge_types:
            badge = Badge(
                user_id=user.id,
                badge_type='week_10',
                name='⭐ 週間マスター',
                description='1週間で10回のポモドーロを完了'
            )
            db.session.add(badge)
            new_badges.append(badge)
        
        # レベル5達成バッジ
        if user.level >= 5 and 'level_5' not in existing_badge_types:
            badge = Badge(
                user_id=user.id,
                badge_type='level_5',
                name='🌟 レベル5',
                description='レベル5に到達'
            )
            db.session.add(badge)
            new_badges.append(badge)
        
        # レベル10達成バッジ
        if user.level >= 10 and 'level_10' not in existing_badge_types:
            badge = Badge(
                user_id=user.id,
                badge_type='level_10',
                name='🌟🌟 レベル10',
                description='レベル10に到達'
            )
            db.session.add(badge)
            new_badges.append(badge)
        
        # 初回完了バッジ
        if user.sessions and len(user.sessions) == 1 and 'first_complete' not in existing_badge_types:
            badge = Badge(
                user_id=user.id,
                badge_type='first_complete',
                name='🎯 はじめの一歩',
                description='初めてのポモドーロを完了'
            )
            db.session.add(badge)
            new_badges.append(badge)
        
        return new_badges

# API Endpoints
@app.route('/')
def index():
    """メイン画面"""
    return render_template('index.html')

@app.route('/api/user')
def get_user():
    """ユーザー情報取得"""
    user = User.query.first()
    if not user:
        user = User(name='Player')
        db.session.add(user)
        db.session.commit()
    
    # 次のレベルまでのXP進捗を計算
    current_level_xp = sum(GamificationEngine.xp_for_level(l) for l in range(1, user.level))
    next_level_xp = GamificationEngine.xp_for_level(user.level)
    xp_in_current_level = user.xp - current_level_xp
    xp_progress_percent = (xp_in_current_level / next_level_xp) * 100
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'xp': user.xp,
        'level': user.level,
        'xp_in_current_level': xp_in_current_level,
        'xp_for_next_level': next_level_xp,
        'xp_progress_percent': xp_progress_percent,
        'current_streak': user.current_streak,
        'longest_streak': user.longest_streak,
        'total_sessions': len(user.sessions)
    })

@app.route('/api/complete-pomodoro', methods=['POST'])
def complete_pomodoro():
    """ポモドーロ完了処理"""
    data = request.json
    duration = data.get('duration', 25)
    task_name = data.get('task_name', '')
    
    user = User.query.first()
    if not user:
        user = User(name='Player')
        db.session.add(user)
        db.session.commit()
    
    # ストリーク更新
    GamificationEngine.update_streak(user)
    
    # XP付与
    xp_result = GamificationEngine.award_xp_for_completion(user, duration)
    
    # セッション記録
    session = PomodoroSession(
        user_id=user.id,
        duration=duration,
        completed=True,
        xp_earned=xp_result['xp_earned'],
        task_name=task_name
    )
    db.session.add(session)
    
    # バッジ確認
    new_badges = GamificationEngine.check_and_award_badges(user)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'xp_result': xp_result,
        'new_badges': [{
            'name': b.name,
            'description': b.description
        } for b in new_badges],
        'streak': user.current_streak
    })

@app.route('/api/badges')
def get_badges():
    """バッジ一覧取得"""
    user = User.query.first()
    if not user:
        return jsonify([])
    
    badges = Badge.query.filter_by(user_id=user.id).order_by(Badge.earned_at.desc()).all()
    return jsonify([{
        'id': b.id,
        'name': b.name,
        'description': b.description,
        'earned_at': b.earned_at.isoformat()
    } for b in badges])

@app.route('/api/statistics')
def get_statistics():
    """統計情報取得"""
    user = User.query.first()
    if not user:
        return jsonify({})
    
    now = datetime.utcnow()
    
    # 週間統計
    week_ago = now - timedelta(days=7)
    week_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == user.id,
        PomodoroSession.completed == True,
        PomodoroSession.completed_at >= week_ago
    ).all()
    
    # 月間統計
    month_ago = now - timedelta(days=30)
    month_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == user.id,
        PomodoroSession.completed == True,
        PomodoroSession.completed_at >= month_ago
    ).all()
    
    # 日別完了数（過去7日間）
    daily_completions = []
    for i in range(6, -1, -1):
        date = now - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        count = PomodoroSession.query.filter(
            PomodoroSession.user_id == user.id,
            PomodoroSession.completed == True,
            PomodoroSession.completed_at >= date_start,
            PomodoroSession.completed_at < date_end
        ).count()
        
        daily_completions.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })
    
    # 平均集中時間
    avg_duration_week = sum(s.duration for s in week_sessions) / len(week_sessions) if week_sessions else 0
    avg_duration_month = sum(s.duration for s in month_sessions) / len(month_sessions) if month_sessions else 0
    
    return jsonify({
        'week': {
            'total_sessions': len(week_sessions),
            'total_minutes': sum(s.duration for s in week_sessions),
            'avg_duration': round(avg_duration_week, 1)
        },
        'month': {
            'total_sessions': len(month_sessions),
            'total_minutes': sum(s.duration for s in month_sessions),
            'avg_duration': round(avg_duration_month, 1)
        },
        'daily_completions': daily_completions
    })

@app.route('/api/history')
def get_history():
    """セッション履歴取得"""
    user = User.query.first()
    if not user:
        return jsonify([])
    
    sessions = PomodoroSession.query.filter_by(
        user_id=user.id,
        completed=True
    ).order_by(PomodoroSession.completed_at.desc()).limit(20).all()
    
    return jsonify([{
        'id': s.id,
        'duration': s.duration,
        'xp_earned': s.xp_earned,
        'task_name': s.task_name,
        'completed_at': s.completed_at.isoformat()
    } for s in sessions])

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
