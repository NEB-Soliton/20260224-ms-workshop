"""Test fixtures and configuration for Pomodoro Timer tests."""
import pytest
from app import create_app
from models import db, User
from config import TestConfig


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username='testuser')
        db.session.add(user)
        db.session.commit()
        # Refresh to get the ID
        db.session.refresh(user)
        return user.id
