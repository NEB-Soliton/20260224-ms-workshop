"""ルート定義"""
from flask import render_template


def init_app(app):
    """ルートを登録"""
    
    @app.route('/')
    def index():
        """トップ画面"""
        return render_template('index.html')
