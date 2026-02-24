"""
Pomodoro Timer App - Flask Backend API
Phase 4: Settings and Session History API Implementation
"""
import os
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dateutil import parser as date_parser

# Initialize Flask app and database
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///pomodoro.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database Models
class Settings(db.Model):
    """User settings model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False, default='default_user')
    work_duration = db.Column(db.Integer, nullable=False, default=25)  # minutes
    break_duration = db.Column(db.Integer, nullable=False, default=5)  # minutes
    long_break_duration = db.Column(db.Integer, nullable=False, default=15)  # minutes
    sessions_before_long_break = db.Column(db.Integer, nullable=False, default=4)
    auto_start_breaks = db.Column(db.Boolean, nullable=False, default=False)
    auto_start_pomodoros = db.Column(db.Boolean, nullable=False, default=False)
    sound_enabled = db.Column(db.Boolean, nullable=False, default=True)
    sound_volume = db.Column(db.Integer, nullable=False, default=50)  # 0-100
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert settings to dictionary"""
        return {
            'user_id': self.user_id,
            'work_duration': self.work_duration,
            'break_duration': self.break_duration,
            'long_break_duration': self.long_break_duration,
            'sessions_before_long_break': self.sessions_before_long_break,
            'auto_start_breaks': self.auto_start_breaks,
            'auto_start_pomodoros': self.auto_start_pomodoros,
            'sound_enabled': self.sound_enabled,
            'sound_volume': self.sound_volume
        }


class PomodoroSession(db.Model):
    """Pomodoro session history model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, default='default_user')
    session_type = db.Column(db.String(20), nullable=False)  # 'work', 'break', 'long_break'
    duration = db.Column(db.Integer, nullable=False)  # minutes
    completed = db.Column(db.Boolean, nullable=False, default=True)
    task_name = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'duration': self.duration,
            'completed': self.completed,
            'task_name': self.task_name,
            'notes': self.notes,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }


# Error handling utilities
def create_error_response(message, status_code=400, error_type='ValidationError'):
    """Create unified error response"""
    return jsonify({
        'error': {
            'type': error_type,
            'message': message,
            'status_code': status_code
        }
    }), status_code


def validate_settings_data(data):
    """Validate settings data"""
    errors = []
    
    # Validate work_duration
    if 'work_duration' in data:
        if not isinstance(data['work_duration'], int) or data['work_duration'] < 1 or data['work_duration'] > 120:
            errors.append('work_duration must be between 1 and 120 minutes')
    
    # Validate break_duration
    if 'break_duration' in data:
        if not isinstance(data['break_duration'], int) or data['break_duration'] < 1 or data['break_duration'] > 60:
            errors.append('break_duration must be between 1 and 60 minutes')
    
    # Validate long_break_duration
    if 'long_break_duration' in data:
        if not isinstance(data['long_break_duration'], int) or data['long_break_duration'] < 1 or data['long_break_duration'] > 60:
            errors.append('long_break_duration must be between 1 and 60 minutes')
    
    # Validate sessions_before_long_break
    if 'sessions_before_long_break' in data:
        if not isinstance(data['sessions_before_long_break'], int) or data['sessions_before_long_break'] < 2 or data['sessions_before_long_break'] > 10:
            errors.append('sessions_before_long_break must be between 2 and 10')
    
    # Validate boolean fields
    bool_fields = ['auto_start_breaks', 'auto_start_pomodoros', 'sound_enabled']
    for field in bool_fields:
        if field in data and not isinstance(data[field], bool):
            errors.append(f'{field} must be a boolean')
    
    # Validate sound_volume
    if 'sound_volume' in data:
        if not isinstance(data['sound_volume'], int) or data['sound_volume'] < 0 or data['sound_volume'] > 100:
            errors.append('sound_volume must be between 0 and 100')
    
    return errors


def validate_session_data(data):
    """Validate session data"""
    errors = []
    
    # Required fields
    required_fields = ['session_type', 'duration', 'started_at', 'ended_at']
    for field in required_fields:
        if field not in data:
            errors.append(f'{field} is required')
    
    if errors:
        return errors
    
    # Validate session_type
    valid_types = ['work', 'break', 'long_break']
    if data['session_type'] not in valid_types:
        errors.append(f'session_type must be one of: {", ".join(valid_types)}')
    
    # Validate duration
    if not isinstance(data['duration'], int) or data['duration'] < 1:
        errors.append('duration must be a positive integer')
    
    # Validate completed
    if 'completed' in data and not isinstance(data['completed'], bool):
        errors.append('completed must be a boolean')
    
    # Validate datetime fields
    for field in ['started_at', 'ended_at']:
        try:
            date_parser.parse(data[field])
        except (ValueError, TypeError):
            errors.append(f'{field} must be a valid ISO 8601 datetime string')
    
    # Validate task_name length
    if 'task_name' in data and data['task_name'] and len(data['task_name']) > 200:
        errors.append('task_name must be 200 characters or less')
    
    return errors


# API Routes

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current user settings"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        settings = Settings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            # Return default settings if none exist
            settings = Settings(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': settings.to_dict()
        }), 200
    
    except Exception as e:
        return create_error_response(
            f'Failed to retrieve settings: {str(e)}',
            status_code=500,
            error_type='ServerError'
        )


@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update user settings"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return create_error_response('Request body is required')
        
        # Validate data
        validation_errors = validate_settings_data(data)
        if validation_errors:
            return create_error_response(
                'Validation failed: ' + '; '.join(validation_errors)
            )
        
        # Get or create settings
        user_id = data.get('user_id', 'default_user')
        settings = Settings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            settings = Settings(user_id=user_id)
            db.session.add(settings)
        
        # Update settings
        for key, value in data.items():
            if key != 'user_id' and hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully',
            'data': settings.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return create_error_response(
            f'Failed to update settings: {str(e)}',
            status_code=500,
            error_type='ServerError'
        )


@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new pomodoro session"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return create_error_response('Request body is required')
        
        # Validate data
        validation_errors = validate_session_data(data)
        if validation_errors:
            return create_error_response(
                'Validation failed: ' + '; '.join(validation_errors)
            )
        
        # Parse datetime fields
        started_at = date_parser.parse(data['started_at'])
        ended_at = date_parser.parse(data['ended_at'])
        
        # Create session
        session = PomodoroSession(
            user_id=data.get('user_id', 'default_user'),
            session_type=data['session_type'],
            duration=data['duration'],
            completed=data.get('completed', True),
            task_name=data.get('task_name'),
            notes=data.get('notes'),
            started_at=started_at,
            ended_at=ended_at
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session created successfully',
            'data': session.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return create_error_response(
            f'Failed to create session: {str(e)}',
            status_code=500,
            error_type='ServerError'
        )


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get pomodoro sessions, optionally filtered by date"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        date_str = request.args.get('date')
        
        # Build query
        query = PomodoroSession.query.filter_by(user_id=user_id)
        
        # Filter by date if provided
        if date_str:
            try:
                # Parse date string (YYYY-MM-DD)
                filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Filter sessions that started on this date
                query = query.filter(
                    db.func.date(PomodoroSession.started_at) == filter_date
                )
            except ValueError:
                return create_error_response(
                    'Invalid date format. Expected YYYY-MM-DD'
                )
        
        # Get sessions ordered by start time (most recent first)
        sessions = query.order_by(PomodoroSession.started_at.desc()).all()
        
        return jsonify({
            'success': True,
            'count': len(sessions),
            'data': [session.to_dict() for session in sessions]
        }), 200
    
    except Exception as e:
        return create_error_response(
            f'Failed to retrieve sessions: {str(e)}',
            status_code=500,
            error_type='ServerError'
        )


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Pomodoro API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_error_response(
        'Resource not found',
        status_code=404,
        error_type='NotFoundError'
    )


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return create_error_response(
        'Method not allowed',
        status_code=405,
        error_type='MethodNotAllowedError'
    )


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors"""
    return create_error_response(
        'Internal server error',
        status_code=500,
        error_type='ServerError'
    )


# Initialize database
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
