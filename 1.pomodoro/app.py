"""
Pomodoro Timer App - Phase 5: JSON永続化実装
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import sys

# モジュール検索パスにカレントディレクトリを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Settings, PomodoroSession
from repositories import SettingsRepository, HistoryRepository
from services import ProgressService

app = Flask(__name__)

# リポジトリとサービスの初期化
settings_repo = SettingsRepository()
history_repo = HistoryRepository()
progress_service = ProgressService(history_repo)


@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """設定を取得"""
    settings = settings_repo.load()
    return jsonify(settings.to_dict())


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """設定を更新"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    try:
        settings = Settings.from_dict(data)
        settings_repo.save(settings)
        return jsonify({"success": True, "settings": settings.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """履歴を取得"""
    # クエリパラメータで件数を指定可能
    limit = request.args.get('limit', 10, type=int)
    sessions = history_repo.get_recent(limit)
    return jsonify([session.to_dict() for session in sessions])


@app.route('/api/history', methods=['POST'])
def add_session():
    """セッションを追加"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    try:
        # セッションIDがない場合は生成
        if 'id' not in data:
            data['id'] = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # 時刻がない場合は現在時刻を設定
        if 'start_time' not in data:
            data['start_time'] = datetime.now().isoformat()
        if 'end_time' not in data:
            data['end_time'] = datetime.now().isoformat()
        
        session = PomodoroSession.from_dict(data)
        history_repo.add(session)
        return jsonify({"success": True, "session": session.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/progress/today', methods=['GET'])
def get_today_progress():
    """当日の進捗を取得"""
    progress = progress_service.get_today_progress()
    return jsonify(progress.to_dict())


@app.route('/api/progress/weekly', methods=['GET'])
def get_weekly_progress():
    """今週の進捗サマリーを取得"""
    summary = progress_service.get_weekly_summary()
    return jsonify(summary)


if __name__ == '__main__':
    # 開発サーバーを起動
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
