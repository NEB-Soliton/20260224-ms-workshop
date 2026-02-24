"""Pomodoro Timer Application"""
from flask import Flask


def create_app(config=None):
    """アプリケーションファクトリー"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    if config:
        app.config.update(config)
    
    # ルート定義
    from . import routes
    routes.init_app(app)
    
    return app
