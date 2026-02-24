"""API routes for Pomodoro Timer application."""
from flask import Blueprint, jsonify, request
from models import db, User
from services import PomodoroService

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    data = request.get_json()
    
    if not data or 'username' not in data:
        return jsonify({'error': 'Username is required'}), 400
    
    username = data['username']
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409
    
    # Create new user
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'level': user.level,
        'xp': user.xp
    }), 201


@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'level': user.level,
        'xp': user.xp,
        'total_pomodoros': user.total_pomodoros,
        'total_work_time': user.total_work_time,
        'streak_days': user.streak_days
    })


@api.route('/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user statistics."""
    try:
        stats = PomodoroService.get_user_stats(user_id)
        return jsonify(stats)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@api.route('/sessions/start', methods=['POST'])
def start_session():
    """Start a new pomodoro session."""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'duration' not in data:
        return jsonify({'error': 'user_id and duration are required'}), 400
    
    user_id = data['user_id']
    duration = data['duration']
    
    # Validate duration
    if not isinstance(duration, int) or duration <= 0:
        return jsonify({'error': 'Duration must be a positive integer'}), 400
    
    try:
        session = PomodoroService.start_session(user_id, duration)
        return jsonify({
            'session_id': session.id,
            'user_id': session.user_id,
            'duration': session.duration,
            'started_at': session.started_at.isoformat(),
            'completed': session.completed
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@api.route('/sessions/<int:session_id>/complete', methods=['POST'])
def complete_session(session_id):
    """Complete a pomodoro session."""
    try:
        result = PomodoroService.complete_session(session_id)
        
        return jsonify({
            'session_id': result['session'].id,
            'completed': result['session'].completed,
            'xp_earned': result['xp_earned'],
            'badges_awarded': result['badges_awarded'],
            'new_level': result['new_level']
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@api.route('/users/<int:user_id>/badges', methods=['GET'])
def get_user_badges(user_id):
    """Get user's badges."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    badges = [
        {
            'id': badge.id,
            'name': badge.name,
            'description': badge.description,
            'earned_at': badge.earned_at.isoformat()
        }
        for badge in user.badges
    ]
    
    return jsonify({'badges': badges})
