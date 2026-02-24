"""API contract tests for Pomodoro Timer endpoints."""
import pytest
import json
from models import db, User, PomodoroSession, Badge


class TestUserEndpoints:
    """Test cases for user-related API endpoints."""
    
    def test_create_user_success(self, client):
        """Test creating a new user (positive case)."""
        response = client.post(
            '/api/users',
            data=json.dumps({'username': 'newuser'}),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['username'] == 'newuser'
        assert data['level'] == 1
        assert data['xp'] == 0
        assert 'id' in data
    
    def test_create_user_missing_username(self, client):
        """Test creating user without username (negative case)."""
        response = client.post(
            '/api/users',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Username is required' in data['error']
    
    def test_create_user_duplicate_username(self, client, test_user):
        """Test creating user with existing username (negative case)."""
        response = client.post(
            '/api/users',
            data=json.dumps({'username': 'testuser'}),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'already exists' in data['error']
    
    def test_create_user_invalid_json(self, client):
        """Test creating user with invalid JSON (negative case)."""
        response = client.post(
            '/api/users',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_get_user_success(self, client, test_user):
        """Test getting user details (positive case)."""
        response = client.get(f'/api/users/{test_user}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_user
        assert data['username'] == 'testuser'
        assert 'level' in data
        assert 'xp' in data
        assert 'total_pomodoros' in data
        assert 'total_work_time' in data
        assert 'streak_days' in data
    
    def test_get_user_not_found(self, client):
        """Test getting non-existent user (negative case)."""
        response = client.get('/api/users/999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_get_user_stats_success(self, client, test_user, app):
        """Test getting user statistics (positive case)."""
        # Add some test data
        with app.app_context():
            user = User.query.get(test_user)
            user.total_pomodoros = 5
            session = PomodoroSession(user_id=test_user, duration=25, completed=True)
            db.session.add(session)
            db.session.commit()
        
        response = client.get(f'/api/users/{test_user}/stats')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'testuser'
        assert 'level' in data
        assert 'xp' in data
        assert 'total_pomodoros' in data
        assert 'completed_sessions' in data
        assert 'badges_count' in data
    
    def test_get_user_stats_not_found(self, client):
        """Test getting stats for non-existent user (negative case)."""
        response = client.get('/api/users/999/stats')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestSessionEndpoints:
    """Test cases for session-related API endpoints."""
    
    def test_start_session_success(self, client, test_user):
        """Test starting a new session (positive case)."""
        response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': test_user, 'duration': 25}),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['user_id'] == test_user
        assert data['duration'] == 25
        assert data['completed'] is False
        assert 'session_id' in data
        assert 'started_at' in data
    
    def test_start_session_missing_user_id(self, client):
        """Test starting session without user_id (negative case)."""
        response = client.post(
            '/api/sessions/start',
            data=json.dumps({'duration': 25}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'user_id' in data['error']
    
    def test_start_session_missing_duration(self, client, test_user):
        """Test starting session without duration (negative case)."""
        response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': test_user}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'duration' in data['error']
    
    def test_start_session_invalid_duration(self, client, test_user):
        """Test starting session with invalid duration (negative case)."""
        # Negative duration
        response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': test_user, 'duration': -5}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Zero duration
        response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': test_user, 'duration': 0}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Non-integer duration
        response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': test_user, 'duration': 'twenty-five'}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_start_session_invalid_user(self, client):
        """Test starting session with non-existent user (negative case)."""
        response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': 999, 'duration': 25}),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_complete_session_success(self, client, test_user):
        """Test completing a session (positive case)."""
        # Start a session first
        start_response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': test_user, 'duration': 25}),
            content_type='application/json'
        )
        session_id = start_response.get_json()['session_id']
        
        # Complete the session
        response = client.post(f'/api/sessions/{session_id}/complete')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['session_id'] == session_id
        assert data['completed'] is True
        assert 'xp_earned' in data
        assert 'badges_awarded' in data
        assert 'new_level' in data
        assert data['xp_earned'] > 0
    
    def test_complete_session_not_found(self, client):
        """Test completing non-existent session (negative case)."""
        response = client.post('/api/sessions/999/complete')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_complete_session_already_completed(self, client, test_user):
        """Test completing already completed session (negative case)."""
        # Start and complete a session
        start_response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': test_user, 'duration': 25}),
            content_type='application/json'
        )
        session_id = start_response.get_json()['session_id']
        client.post(f'/api/sessions/{session_id}/complete')
        
        # Try to complete again
        response = client.post(f'/api/sessions/{session_id}/complete')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestBadgeEndpoints:
    """Test cases for badge-related API endpoints."""
    
    def test_get_user_badges_success(self, client, test_user, app):
        """Test getting user badges (positive case)."""
        # Add some badges
        with app.app_context():
            badge1 = Badge(user_id=test_user, name='Badge 1', description='First badge')
            badge2 = Badge(user_id=test_user, name='Badge 2', description='Second badge')
            db.session.add_all([badge1, badge2])
            db.session.commit()
        
        response = client.get(f'/api/users/{test_user}/badges')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'badges' in data
        assert len(data['badges']) == 2
        
        # Check badge structure
        badge = data['badges'][0]
        assert 'id' in badge
        assert 'name' in badge
        assert 'description' in badge
        assert 'earned_at' in badge
    
    def test_get_user_badges_empty(self, client, test_user):
        """Test getting badges for user with no badges (positive case)."""
        response = client.get(f'/api/users/{test_user}/badges')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'badges' in data
        assert len(data['badges']) == 0
    
    def test_get_user_badges_not_found(self, client):
        """Test getting badges for non-existent user (negative case)."""
        response = client.get('/api/users/999/badges')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestIntegrationFlow:
    """Integration tests for complete workflows."""
    
    def test_complete_pomodoro_workflow(self, client):
        """Test complete pomodoro workflow from user creation to completion."""
        # 1. Create a user
        response = client.post(
            '/api/users',
            data=json.dumps({'username': 'flowuser'}),
            content_type='application/json'
        )
        assert response.status_code == 201
        user_id = response.get_json()['id']
        
        # 2. Start a session
        response = client.post(
            '/api/sessions/start',
            data=json.dumps({'user_id': user_id, 'duration': 25}),
            content_type='application/json'
        )
        assert response.status_code == 201
        session_id = response.get_json()['session_id']
        
        # 3. Complete the session
        response = client.post(f'/api/sessions/{session_id}/complete')
        assert response.status_code == 200
        data = response.get_json()
        assert data['completed'] is True
        assert len(data['badges_awarded']) > 0  # Should get first pomodoro badge
        
        # 4. Check user stats
        response = client.get(f'/api/users/{user_id}/stats')
        assert response.status_code == 200
        stats = response.get_json()
        assert stats['total_pomodoros'] == 1
        assert stats['completed_sessions'] == 1
        assert stats['badges_count'] == 1
        
        # 5. Check badges
        response = client.get(f'/api/users/{user_id}/badges')
        assert response.status_code == 200
        badges = response.get_json()['badges']
        assert len(badges) == 1
        assert badges[0]['name'] == 'First Pomodoro'
    
    def test_multiple_sessions_workflow(self, client):
        """Test completing multiple sessions and earning badges."""
        # Create user
        response = client.post(
            '/api/users',
            data=json.dumps({'username': 'multiuser'}),
            content_type='application/json'
        )
        user_id = response.get_json()['id']
        
        # Complete 10 sessions to earn "Dedicated" badge
        for i in range(10):
            # Start session
            response = client.post(
                '/api/sessions/start',
                data=json.dumps({'user_id': user_id, 'duration': 25}),
                content_type='application/json'
            )
            session_id = response.get_json()['session_id']
            
            # Complete session
            response = client.post(f'/api/sessions/{session_id}/complete')
            assert response.status_code == 200
        
        # Check final stats
        response = client.get(f'/api/users/{user_id}/stats')
        stats = response.get_json()
        assert stats['total_pomodoros'] == 10
        assert stats['badges_count'] >= 2  # First Pomodoro + Dedicated
