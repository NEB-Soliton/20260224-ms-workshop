"""
API Contract Tests - Normal and Error Cases
API契約テスト（正常系/異常系）
"""
import pytest
import json
from datetime import datetime, timedelta


class TestSettingsAPI:
    """Test suite for Settings API endpoints"""
    
    def test_get_settings_success(self, client, reset_storage):
        """Test GET /api/settings returns default settings"""
        response = client.get('/api/settings')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'workDuration' in data
        assert 'breakDuration' in data
        assert 'theme' in data
        assert 'soundEnabled' in data
        
        # Check default values
        assert data['workDuration'] == 25
        assert data['breakDuration'] == 5
        assert data['theme'] == 'light'
        assert data['soundEnabled'] is True
    
    def test_update_settings_success(self, client, reset_storage):
        """Test PUT /api/settings with valid data"""
        new_settings = {
            'workDuration': 30,
            'breakDuration': 10,
            'theme': 'dark',
            'soundEnabled': False
        }
        
        response = client.put(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['workDuration'] == 30
        assert data['breakDuration'] == 10
        assert data['theme'] == 'dark'
        assert data['soundEnabled'] is False
    
    def test_update_settings_partial(self, client, reset_storage):
        """Test PUT /api/settings with partial data"""
        partial_update = {
            'workDuration': 45
        }
        
        response = client.put(
            '/api/settings',
            data=json.dumps(partial_update),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Updated field
        assert data['workDuration'] == 45
        
        # Unchanged fields
        assert data['breakDuration'] == 5
        assert data['theme'] == 'light'
        assert data['soundEnabled'] is True
    
    def test_update_settings_no_data(self, client, reset_storage):
        """Test PUT /api/settings with no data (error case)"""
        response = client.put(
            '/api/settings',
            data=None,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data is not None
        assert 'error' in data
    
    def test_update_settings_invalid_work_duration(self, client, reset_storage):
        """Test PUT /api/settings with invalid workDuration"""
        # Negative value
        response = client.put(
            '/api/settings',
            data=json.dumps({'workDuration': -5}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Zero value
        response = client.put(
            '/api/settings',
            data=json.dumps({'workDuration': 0}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # String value
        response = client.put(
            '/api/settings',
            data=json.dumps({'workDuration': 'invalid'}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_update_settings_invalid_break_duration(self, client, reset_storage):
        """Test PUT /api/settings with invalid breakDuration"""
        response = client.put(
            '/api/settings',
            data=json.dumps({'breakDuration': -10}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_update_settings_invalid_theme(self, client, reset_storage):
        """Test PUT /api/settings with invalid theme"""
        response = client.put(
            '/api/settings',
            data=json.dumps({'theme': 'invalid_theme'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'theme' in data['error'].lower()
    
    def test_update_settings_invalid_sound_enabled(self, client, reset_storage):
        """Test PUT /api/settings with invalid soundEnabled"""
        response = client.put(
            '/api/settings',
            data=json.dumps({'soundEnabled': 'yes'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestSessionsAPI:
    """Test suite for Sessions API endpoints"""
    
    def test_create_session_success(self, client, reset_storage):
        """Test POST /api/sessions with valid data"""
        session_data = {
            'duration': 25,
            'completed': True,
            'mode': 'work'
        }
        
        response = client.post(
            '/api/sessions',
            data=json.dumps(session_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['id'] == 1
        assert data['duration'] == 25
        assert data['completed'] is True
        assert data['mode'] == 'work'
        assert 'timestamp' in data
        assert 'rewards' in data  # Should have rewards for completed session
    
    def test_create_session_incomplete(self, client, reset_storage):
        """Test POST /api/sessions with incomplete session"""
        session_data = {
            'duration': 15,
            'completed': False
        }
        
        response = client.post(
            '/api/sessions',
            data=json.dumps(session_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['completed'] is False
        assert 'rewards' not in data  # No rewards for incomplete session
    
    def test_create_session_no_data(self, client, reset_storage):
        """Test POST /api/sessions with no data (error case)"""
        response = client.post(
            '/api/sessions',
            data=None,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data is not None
        assert 'error' in data
    
    def test_create_session_missing_duration(self, client, reset_storage):
        """Test POST /api/sessions missing duration field"""
        session_data = {
            'completed': True
        }
        
        response = client.post(
            '/api/sessions',
            data=json.dumps(session_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'duration' in data['error'].lower()
    
    def test_create_session_missing_completed(self, client, reset_storage):
        """Test POST /api/sessions missing completed field"""
        session_data = {
            'duration': 25
        }
        
        response = client.post(
            '/api/sessions',
            data=json.dumps(session_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_session_invalid_duration(self, client, reset_storage):
        """Test POST /api/sessions with invalid duration"""
        # Negative duration
        response = client.post(
            '/api/sessions',
            data=json.dumps({'duration': -5, 'completed': True}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Zero duration
        response = client.post(
            '/api/sessions',
            data=json.dumps({'duration': 0, 'completed': True}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_create_session_invalid_completed(self, client, reset_storage):
        """Test POST /api/sessions with invalid completed field"""
        response = client.post(
            '/api/sessions',
            data=json.dumps({'duration': 25, 'completed': 'yes'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_get_sessions_empty(self, client, reset_storage):
        """Test GET /api/sessions with no sessions"""
        response = client.get('/api/sessions')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_sessions_with_data(self, client, reset_storage):
        """Test GET /api/sessions returns all sessions"""
        # Create some sessions
        for i in range(3):
            client.post(
                '/api/sessions',
                data=json.dumps({'duration': 25, 'completed': True}),
                content_type='application/json'
            )
        
        response = client.get('/api/sessions')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3
    
    def test_get_sessions_by_date_success(self, client, reset_storage):
        """Test GET /api/sessions with date filter"""
        today = datetime.utcnow().date().isoformat()
        yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
        
        # Create sessions for today
        client.post(
            '/api/sessions',
            data=json.dumps({
                'duration': 25,
                'completed': True,
                'timestamp': datetime.utcnow().isoformat()
            }),
            content_type='application/json'
        )
        
        # Create sessions for yesterday
        client.post(
            '/api/sessions',
            data=json.dumps({
                'duration': 25,
                'completed': True,
                'timestamp': (datetime.utcnow() - timedelta(days=1)).isoformat()
            }),
            content_type='application/json'
        )
        
        # Get today's sessions
        response = client.get(f'/api/sessions?date={today}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
    
    def test_get_sessions_by_date_invalid_format(self, client, reset_storage):
        """Test GET /api/sessions with invalid date format"""
        response = client.get('/api/sessions?date=invalid-date')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'date format' in data['error'].lower()
    
    def test_get_sessions_stats(self, client, reset_storage):
        """Test GET /api/sessions/stats"""
        # Create some sessions
        client.post(
            '/api/sessions',
            data=json.dumps({'duration': 25, 'completed': True, 'mode': 'work'}),
            content_type='application/json'
        )
        client.post(
            '/api/sessions',
            data=json.dumps({'duration': 5, 'completed': False, 'mode': 'break'}),
            content_type='application/json'
        )
        
        response = client.get('/api/sessions/stats')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'total_sessions' in data
        assert 'completed_sessions' in data
        assert 'total_work_time' in data
        assert 'completion_rate' in data
        
        assert data['total_sessions'] == 2
        assert data['completed_sessions'] == 1
        assert data['total_work_time'] == 25
        assert data['completion_rate'] == 0.5


class TestAPIIntegration:
    """Integration tests for API workflows"""
    
    def test_full_pomodoro_workflow(self, client, reset_storage):
        """Test complete Pomodoro workflow"""
        # 1. Get initial settings
        response = client.get('/api/settings')
        assert response.status_code == 200
        
        # 2. Update settings
        response = client.put(
            '/api/settings',
            data=json.dumps({'workDuration': 30}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 3. Complete a work session
        response = client.post(
            '/api/sessions',
            data=json.dumps({
                'duration': 30,
                'completed': True,
                'mode': 'work'
            }),
            content_type='application/json'
        )
        assert response.status_code == 201
        session = response.get_json()
        assert 'rewards' in session
        
        # 4. Get session stats
        response = client.get('/api/sessions/stats')
        assert response.status_code == 200
        stats = response.get_json()
        assert stats['completed_sessions'] == 1
    
    def test_multiple_sessions_rewards(self, client, reset_storage):
        """Test that rewards increase with multiple sessions"""
        # Complete first session
        response1 = client.post(
            '/api/sessions',
            data=json.dumps({'duration': 25, 'completed': True}),
            content_type='application/json'
        )
        rewards1 = response1.get_json()['rewards']
        
        # Complete second session
        response2 = client.post(
            '/api/sessions',
            data=json.dumps({'duration': 25, 'completed': True}),
            content_type='application/json'
        )
        rewards2 = response2.get_json()['rewards']
        
        # Verify rewards increased
        assert rewards2['xp'] > rewards1['xp']
        assert rewards2['completed_count'] > rewards1['completed_count']
