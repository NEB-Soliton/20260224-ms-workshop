# ポモドーロタイマーアプリケーション

Phase 6: テスト整備完了版

## 概要

このポモドーロタイマーアプリケーションは、ゲーミフィケーション機能を備えた生産性向上ツールです。
経験値、レベル、バッジ、ストリークなどの要素でモチベーションを維持します。

## 機能

### コア機能
- ⏱️ ポモドーロタイマー (作業/休憩モード)
- 🎮 ゲーミフィケーション (XP、レベル、バッジ)
- 📊 セッション履歴と統計
- ⚙️ カスタマイズ可能な設定

### ゲーミフィケーション
- **経験値システム**: 完了ごとに 100 XP
- **レベルアップ**: レベル × 200 XP で次のレベルへ
- **ストリークボーナス**:
  - 3日連続: +50 XP
  - 7日連続: +100 XP
- **バッジ**:
  - 初心者 (10回完了)
  - 中級者 (50回完了)
  - 上級者 (100回完了)
  - 3日連続、7日連続

## 技術スタック

### バックエンド
- **Framework**: Flask 3.0.0
- **Pattern**: Application Factory
- **Language**: Python 3.12+

### フロントエンド
- **UI**: HTML5 + CSS3
- **Logic**: Vanilla JavaScript
- **Timer Engine**: 状態機械パターン

### テスト
- **Framework**: pytest 8.0.0
- **Coverage**: pytest-cov 4.1.0
- **Flask Testing**: pytest-flask 1.3.0
- **Coverage**: 98%

## セットアップ

### 必要要件
- Python 3.12+
- pip

### インストール

```bash
cd 1.pomodoro
pip install -r requirements.txt
```

## 使い方

### アプリケーションの起動

```bash
python app.py
```

ブラウザで http://localhost:5000 を開きます。

### 開発モードで起動

```bash
export FLASK_DEBUG=true
python app.py
```

## テスト

### すべてのテストを実行

```bash
pytest tests/ -v
```

### カバレッジ付きで実行

```bash
pytest tests/ -v --cov=pomodoro --cov-report=html
```

HTMLレポートは `htmlcov/index.html` で確認できます。

### 特定のテストのみ実行

```bash
# サービス層のテスト
pytest tests/test_services.py -v

# API テスト
pytest tests/test_api.py -v

# アプリケーションテスト
pytest tests/test_app.py -v
```

## API エンドポイント

### 設定

#### GET /api/settings
現在の設定を取得

```bash
curl http://localhost:5000/api/settings
```

#### PUT /api/settings
設定を更新

```bash
curl -X PUT http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"workDuration": 30, "theme": "dark"}'
```

### セッション

#### POST /api/sessions
セッションを記録

```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"duration": 25, "completed": true, "mode": "work"}'
```

#### GET /api/sessions
セッション一覧を取得

```bash
# すべてのセッション
curl http://localhost:5000/api/sessions

# 日付フィルタ
curl http://localhost:5000/api/sessions?date=2026-02-24
```

#### GET /api/sessions/stats
統計情報を取得

```bash
curl http://localhost:5000/api/sessions/stats
```

## プロジェクト構造

```
1.pomodoro/
├── app.py                      # アプリケーションエントリポイント
├── pomodoro/                   # メインパッケージ
│   ├── __init__.py            # Application Factory
│   ├── api.py                 # REST API エンドポイント
│   ├── services.py            # ビジネスロジック (GamificationEngine)
│   └── views.py               # ビューハンドラ
├── static/                     # 静的ファイル
│   ├── css/
│   │   └── style.css          # スタイルシート
│   └── js/
│       └── timer_engine.js    # タイマーエンジン
├── templates/                  # HTML テンプレート
│   └── index.html             # メインページ
├── tests/                      # テストスイート
│   ├── conftest.py            # pytest 設定
│   ├── test_app.py            # アプリケーションテスト
│   ├── test_api.py            # API テスト
│   ├── test_services.py       # サービス層テスト
│   ├── TEST_REPORT.md         # テストレポート
│   └── README_JAVASCRIPT_TESTS.md  # JS テストガイド
├── requirements.txt            # Python 依存関係
└── pyproject.toml             # pytest 設定
```

## テスト結果

### サマリー
- **総テスト数**: 45
- **成功**: 45 (100%)
- **失敗**: 0
- **コードカバレッジ**: 98%

### カバレッジ詳細

```
Name                   Stmts   Miss  Cover
------------------------------------------
pomodoro/__init__.py      17      0   100%
pomodoro/api.py           70      2    97%
pomodoro/services.py      70      1    99%
pomodoro/views.py          5      0   100%
------------------------------------------
TOTAL                    162      3    98%
```

## 開発ガイドライン

### コーディング規約
- PEP 8 に準拠
- 型ヒントの使用を推奨
- docstring は必須

### テスト規約
- 新機能には必ずテストを追加
- カバレッジ 90% 以上を維持
- テストファイル名は `test_*.py`
- テスト関数名は `test_*`

### コミット規約
- コミットメッセージは日本語または英語
- 変更内容を明確に記述

## トラブルシューティング

### テストが失敗する
```bash
# キャッシュをクリア
rm -rf .pytest_cache __pycache__

# 依存関係を再インストール
pip install -r requirements.txt --force-reinstall
```

### ポートが使用中
```bash
# 別のポートで起動
PORT=8000 python app.py
```

### カバレッジレポートが生成されない
```bash
# カバレッジを明示的に指定
pytest tests/ --cov=pomodoro --cov-report=html --cov-report=term
```

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 貢献

バグ報告、機能リクエスト、プルリクエストを歓迎します。

## 参考資料

- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Pomodoro Technique](https://en.wikipedia.org/wiki/Pomodoro_Technique)
