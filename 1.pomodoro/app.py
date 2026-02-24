"""
Pomodoro Timer App
Phase 0: 初期セットアップ - 最小構成のFlaskアプリケーション
"""
from flask import Flask, render_template


def create_app():
    """アプリケーションファクトリ"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """トップ画面を返却"""
        return render_template('index.html')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
