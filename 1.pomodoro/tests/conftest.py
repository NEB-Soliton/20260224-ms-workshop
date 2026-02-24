"""
Test configuration and fixtures
テスト設定とフィクスチャ
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pomodoro import create_app


@pytest.fixture
def app():
    """Create and configure a test Flask application instance"""
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'DEBUG': False
    })
    
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture
def reset_storage():
    """Reset API storage before each test"""
    from pomodoro.api import _storage
    
    # Save original state
    original_settings = _storage['settings'].copy()
    original_sessions = _storage['sessions'].copy()
    
    # Reset to default
    _storage['settings'] = {
        'workDuration': 25,
        'breakDuration': 5,
        'theme': 'light',
        'soundEnabled': True
    }
    _storage['sessions'] = []
    
    yield _storage
    
    # Restore original state
    _storage['settings'] = original_settings
    _storage['sessions'] = original_sessions
