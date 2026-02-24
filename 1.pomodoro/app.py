"""Pomodoro Timer App with JSON Persistence"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os

from models import Settings, PomodoroSession
from repositories import SettingsRepository, SessionRepository
from services import StatisticsService

app = Flask(__name__)

# データディレクトリのパスを設定
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# リポジトリとサービスの初期化
settings_repo = SettingsRepository(DATA_DIR)
session_repo = SessionRepository(DATA_DIR)
stats_service = StatisticsService(session_repo)


# ===== ルート =====

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


# ===== 設定API =====

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """設定を取得"""
    settings = settings_repo.load()
    return jsonify(settings.to_dict())


@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """設定を更新"""
    data = request.get_json()
    settings = settings_repo.load()
    
    # 更新可能なフィールドのみを更新
    for key, value in data.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    if settings_repo.save(settings):
        return jsonify(settings.to_dict())
    else:
        return jsonify({"error": "設定の保存に失敗しました"}), 500


@app.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    """設定をデフォルトにリセット"""
    settings = settings_repo.reset()
    return jsonify(settings.to_dict())


# ===== セッションAPI =====

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """セッション履歴を取得"""
    date = request.args.get('date')
    
    if date:
        sessions = session_repo.get_by_date(date)
    else:
        sessions = session_repo.load_all()
    
    return jsonify([s.to_dict() for s in sessions])


@app.route('/api/sessions/today', methods=['GET'])
def get_today_sessions():
    """今日のセッション履歴を取得"""
    sessions = session_repo.get_today()
    return jsonify([s.to_dict() for s in sessions])


@app.route('/api/sessions', methods=['POST'])
def add_session():
    """新しいセッションを追加"""
    data = request.get_json()
    
    # 必須フィールドの検証
    required_fields = ['start_time', 'end_time', 'duration', 'session_type']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "必須フィールドが不足しています"}), 400
    
    session = PomodoroSession.from_dict(data)
    
    if session_repo.add(session):
        return jsonify(session.to_dict()), 201
    else:
        return jsonify({"error": "セッションの保存に失敗しました"}), 500


@app.route('/api/sessions/clear', methods=['DELETE'])
def clear_sessions():
    """全てのセッション履歴を削除"""
    if session_repo.clear_all():
        return jsonify({"message": "セッション履歴を削除しました"})
    else:
        return jsonify({"error": "セッション履歴の削除に失敗しました"}), 500


# ===== 統計API =====

@app.route('/api/stats/today', methods=['GET'])
def get_today_stats():
    """今日の統計情報を取得"""
    stats = stats_service.get_today_stats()
    return jsonify(stats)


@app.route('/api/stats/week', methods=['GET'])
def get_week_stats():
    """今週の統計情報を取得"""
    stats = stats_service.get_week_stats()
    return jsonify(stats)


@app.route('/api/stats/history', methods=['GET'])
def get_stats_history():
    """日別の統計履歴を取得"""
    days = request.args.get('days', default=7, type=int)
    history = stats_service.get_daily_history(days)
    return jsonify(history)


if __name__ == '__main__':
    # デバッグモードで起動（開発時のみ）
    app.run(debug=True, host='0.0.0.0', port=5000)
