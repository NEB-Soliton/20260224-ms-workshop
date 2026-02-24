"""
Pomodoro Timer Application
ポモドーロタイマーアプリケーション
"""
from flask import Flask
import os


def create_app(config=None):
    """Application factory for Pomodoro Timer"""
    # Get the absolute path to this file's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Templates and static folders are one level up from pomodoro module
    templates_dir = os.path.join(os.path.dirname(base_dir), 'templates')
    static_dir = os.path.join(os.path.dirname(base_dir), 'static')
    
    app = Flask(__name__, 
                template_folder=templates_dir,
                static_folder=static_dir)
    
    # Default configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.config['TESTING'] = False
    
    # Override with custom config
    if config:
        app.config.update(config)
    
    # Register blueprints
    from pomodoro.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from pomodoro.views import views_bp
    app.register_blueprint(views_bp)
    
    return app
