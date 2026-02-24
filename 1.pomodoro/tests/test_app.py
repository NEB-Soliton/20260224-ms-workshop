"""
Test application factory and basic setup
アプリケーションファクトリと基本セットアップのテスト
"""
import pytest
from pomodoro import create_app


def test_create_app():
    """Test that the app factory creates an app instance"""
    app = create_app()
    assert app is not None


def test_create_app_with_config():
    """Test app factory with custom configuration"""
    config = {
        'TESTING': True,
        'SECRET_KEY': 'test-key'
    }
    app = create_app(config)
    
    assert app.config['TESTING'] is True
    assert app.config['SECRET_KEY'] == 'test-key'


def test_app_blueprints_registered(app):
    """Test that required blueprints are registered"""
    # Check that blueprints exist
    assert 'api' in app.blueprints
    assert 'views' in app.blueprints


def test_index_route_exists(client):
    """Test that the index route returns successfully"""
    response = client.get('/')
    assert response.status_code == 200


def test_api_endpoints_exist(client):
    """Test that API endpoints are accessible"""
    # Settings endpoint
    response = client.get('/api/settings')
    assert response.status_code == 200
    
    # Sessions endpoint
    response = client.get('/api/sessions')
    assert response.status_code == 200
