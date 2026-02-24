# Pomodoro Timer API

Phase 4実装: 設定・履歴管理のためのバックエンドAPI

## セットアップ

### 依存関係のインストール

```bash
cd 1.pomodoro
pip install -r requirements.txt
```

### サーバーの起動

```bash
python3 app.py
```

サーバーはデフォルトで `http://localhost:5000` で起動します。

## API エンドポイント

### 1. ヘルスチェック

**GET** `/api/health`

サーバーの動作確認用エンドポイント。

**レスポンス例:**
```json
{
  "success": true,
  "message": "Pomodoro API is running",
  "timestamp": "2026-02-24T06:44:25.968315"
}
```

### 2. 設定の取得

**GET** `/api/settings`

ユーザーの設定を取得します。設定が存在しない場合はデフォルト設定を作成して返します。

**クエリパラメータ:**
- `user_id` (optional): ユーザーID（デフォルト: "default_user"）

**レスポンス例:**
```json
{
  "success": true,
  "data": {
    "user_id": "default_user",
    "work_duration": 25,
    "break_duration": 5,
    "long_break_duration": 15,
    "sessions_before_long_break": 4,
    "auto_start_breaks": false,
    "auto_start_pomodoros": false,
    "sound_enabled": true,
    "sound_volume": 50
  }
}
```

### 3. 設定の更新

**PUT** `/api/settings`

ユーザーの設定を更新します。

**リクエストボディ:**
```json
{
  "work_duration": 30,
  "break_duration": 10,
  "sound_volume": 75,
  "auto_start_breaks": true
}
```

**バリデーションルール:**
- `work_duration`: 1-120分
- `break_duration`: 1-60分
- `long_break_duration`: 1-60分
- `sessions_before_long_break`: 2-10回
- `sound_volume`: 0-100
- Boolean フィールド: `auto_start_breaks`, `auto_start_pomodoros`, `sound_enabled`

**レスポンス例:**
```json
{
  "success": true,
  "message": "Settings updated successfully",
  "data": {
    "user_id": "default_user",
    "work_duration": 30,
    "break_duration": 10,
    "long_break_duration": 15,
    "sessions_before_long_break": 4,
    "auto_start_breaks": true,
    "auto_start_pomodoros": false,
    "sound_enabled": true,
    "sound_volume": 75
  }
}
```

### 4. セッションの作成

**POST** `/api/sessions`

完了したポモドーロセッションを記録します。

**リクエストボディ:**
```json
{
  "session_type": "work",
  "duration": 25,
  "task_name": "タスク名",
  "notes": "メモ",
  "started_at": "2026-02-24T10:00:00Z",
  "ended_at": "2026-02-24T10:25:00Z",
  "completed": true
}
```

**必須フィールド:**
- `session_type`: "work", "break", "long_break" のいずれか
- `duration`: 期間（分）
- `started_at`: 開始時刻（ISO 8601形式）
- `ended_at`: 終了時刻（ISO 8601形式）

**オプションフィールド:**
- `task_name`: タスク名（200文字以内）
- `notes`: メモ
- `completed`: 完了フラグ（デフォルト: true）
- `user_id`: ユーザーID（デフォルト: "default_user"）

**レスポンス例:**
```json
{
  "success": true,
  "message": "Session created successfully",
  "data": {
    "id": 1,
    "user_id": "default_user",
    "session_type": "work",
    "duration": 25,
    "completed": true,
    "task_name": "タスク名",
    "notes": "メモ",
    "started_at": "2026-02-24T10:00:00",
    "ended_at": "2026-02-24T10:25:00",
    "created_at": "2026-02-24T10:25:30.123456"
  }
}
```

### 5. セッション履歴の取得

**GET** `/api/sessions`

セッション履歴を取得します。日付でフィルタリング可能です。

**クエリパラメータ:**
- `user_id` (optional): ユーザーID（デフォルト: "default_user"）
- `date` (optional): 日付フィルター（YYYY-MM-DD形式）

**レスポンス例:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": 2,
      "user_id": "default_user",
      "session_type": "work",
      "duration": 25,
      "completed": true,
      "task_name": "タスク2",
      "notes": null,
      "started_at": "2026-02-24T11:00:00",
      "ended_at": "2026-02-24T11:25:00",
      "created_at": "2026-02-24T11:25:30.123456"
    },
    {
      "id": 1,
      "user_id": "default_user",
      "session_type": "work",
      "duration": 25,
      "completed": true,
      "task_name": "タスク1",
      "notes": null,
      "started_at": "2026-02-24T10:00:00",
      "ended_at": "2026-02-24T10:25:00",
      "created_at": "2026-02-24T10:25:30.123456"
    }
  ]
}
```

## エラー処理

すべてのエラーは統一形式で返されます：

```json
{
  "error": {
    "type": "ValidationError",
    "message": "エラーメッセージ",
    "status_code": 400
  }
}
```

**エラータイプ:**
- `ValidationError`: 入力データのバリデーションエラー（400）
- `NotFoundError`: リソースが見つからない（404）
- `MethodNotAllowedError`: 許可されていないHTTPメソッド（405）
- `ServerError`: サーバー内部エラー（500）

## テスト

APIのテストを実行するには：

```bash
python3 test_api.py
```

## データベース

SQLiteデータベース（`pomodoro.db`）が自動的に作成されます。

### テーブル構造

**settings テーブル:**
- ユーザーごとの設定を保存
- 作業時間、休憩時間、サウンド設定など

**pomodoro_session テーブル:**
- 完了したポモドーロセッションの履歴
- セッションタイプ、期間、タスク名、メモなど

## 環境変数

- `PORT`: サーバーのポート番号（デフォルト: 5000）
- `FLASK_DEBUG`: デバッグモード（デフォルト: False）
- `DATABASE_URL`: データベースURL（デフォルト: sqlite:///pomodoro.db）

## 開発メモ

- CORS有効化済み（フロントエンドからのアクセス可能）
- ISO 8601形式の日時をサポート
- タイムゾーン対応（UTC）
- 入力バリデーション完備
