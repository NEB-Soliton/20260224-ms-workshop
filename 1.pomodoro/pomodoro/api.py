"""
API endpoints for Pomodoro timer
"""
from flask import Blueprint, jsonify, request
from pomodoro.services import GamificationEngine
from datetime import datetime

api_bp = Blueprint('api', __name__)

# In-memory storage (for demo purposes)
_storage = {
    'settings': {
        'workDuration': 25,
        'breakDuration': 5,
        'theme': 'light',
        'soundEnabled': True
    },
    'sessions': []
}


@api_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    return jsonify(_storage['settings'])


@api_bp.route('/settings', methods=['PUT'])
def update_settings():
    """Update settings"""
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validation
    if data is None:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate work duration
    if 'workDuration' in data:
        if not isinstance(data['workDuration'], (int, float)) or data['workDuration'] <= 0:
            return jsonify({'error': 'Invalid workDuration'}), 400
    
    # Validate break duration
    if 'breakDuration' in data:
        if not isinstance(data['breakDuration'], (int, float)) or data['breakDuration'] <= 0:
            return jsonify({'error': 'Invalid breakDuration'}), 400
    
    # Validate theme
    if 'theme' in data:
        if data['theme'] not in ['light', 'dark', 'focus']:
            return jsonify({'error': 'Invalid theme'}), 400
    
    # Validate soundEnabled
    if 'soundEnabled' in data:
        if not isinstance(data['soundEnabled'], bool):
            return jsonify({'error': 'Invalid soundEnabled'}), 400
    
    # Update settings
    _storage['settings'].update(data)
    return jsonify(_storage['settings'])


@api_bp.route('/sessions', methods=['POST'])
def create_session():
    """Record a completed Pomodoro session"""
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validation
    if data is None:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['duration', 'completed']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    if not isinstance(data['duration'], (int, float)) or data['duration'] <= 0:
        return jsonify({'error': 'Invalid duration'}), 400
    
    if not isinstance(data['completed'], bool):
        return jsonify({'error': 'Invalid completed'}), 400
    
    # Create session record
    session = {
        'id': len(_storage['sessions']) + 1,
        'duration': data['duration'],
        'completed': data['completed'],
        'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
        'mode': data.get('mode', 'work')
    }
    
    _storage['sessions'].append(session)
    
    # Calculate gamification rewards if session was completed
    if session['completed']:
        engine = GamificationEngine()
        rewards = engine.calculate_rewards(_storage['sessions'])
        session['rewards'] = rewards
    
    return jsonify(session), 201


@api_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get sessions, optionally filtered by date"""
    date_filter = request.args.get('date')
    
    if date_filter:
        # Filter sessions by date
        try:
            # Parse date in YYYY-MM-DD format
            target_date = datetime.fromisoformat(date_filter).date()
            filtered_sessions = [
                s for s in _storage['sessions']
                if datetime.fromisoformat(s['timestamp']).date() == target_date
            ]
            return jsonify(filtered_sessions)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    return jsonify(_storage['sessions'])


@api_bp.route('/sessions/stats', methods=['GET'])
def get_stats():
    """Get statistics for sessions"""
    sessions = _storage['sessions']
    completed_sessions = [s for s in sessions if s.get('completed', False)]
    
    stats = {
        'total_sessions': len(sessions),
        'completed_sessions': len(completed_sessions),
        'total_work_time': sum(s['duration'] for s in completed_sessions if s.get('mode') == 'work'),
        'completion_rate': len(completed_sessions) / len(sessions) if sessions else 0
    }
    
    return jsonify(stats)
