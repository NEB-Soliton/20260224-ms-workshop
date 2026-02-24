# Pomodoro API クイックリファレンス

## サーバー起動
```bash
cd 1.pomodoro
python3 app.py
```

## API エンドポイント例

### 1. ヘルスチェック
```bash
curl http://localhost:5000/api/health
```

### 2. 設定取得
```bash
curl http://localhost:5000/api/settings
```

### 3. 設定更新
```bash
curl -X PUT http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "work_duration": 30,
    "break_duration": 10,
    "sound_volume": 75,
    "auto_start_breaks": true
  }'
```

### 4. セッション作成
```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "session_type": "work",
    "duration": 25,
    "task_name": "レポート作成",
    "started_at": "2026-02-24T10:00:00Z",
    "ended_at": "2026-02-24T10:25:00Z",
    "completed": true,
    "notes": "集中して作業完了"
  }'
```

### 5. 全セッション取得
```bash
curl http://localhost:5000/api/sessions
```

### 6. 日付指定でセッション取得
```bash
curl "http://localhost:5000/api/sessions?date=2026-02-24"
```

## バリデーションエラー例

### 無効な作業時間
```bash
curl -X PUT http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"work_duration": 200}'
```
**レスポンス:**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Validation failed: work_duration must be between 1 and 120 minutes",
    "status_code": 400
  }
}
```

### 無効なセッションタイプ
```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "session_type": "invalid",
    "duration": 25,
    "started_at": "2026-02-24T10:00:00Z",
    "ended_at": "2026-02-24T10:25:00Z"
  }'
```
**レスポンス:**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Validation failed: session_type must be one of: work, break, long_break",
    "status_code": 400
  }
}
```

### 必須フィールド不足
```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "session_type": "work",
    "duration": 25
  }'
```
**レスポンス:**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Validation failed: started_at is required; ended_at is required",
    "status_code": 400
  }
}
```

### 無効な日付形式
```bash
curl "http://localhost:5000/api/sessions?date=invalid-date"
```
**レスポンス:**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid date format. Expected YYYY-MM-DD",
    "status_code": 400
  }
}
```

## テスト実行
```bash
python3 test_api.py
```

## データモデル

### Settings（設定）
- `work_duration`: 作業時間（1-120分）
- `break_duration`: 休憩時間（1-60分）
- `long_break_duration`: 長休憩時間（1-60分）
- `sessions_before_long_break`: 長休憩までのセッション数（2-10回）
- `auto_start_breaks`: 休憩自動開始
- `auto_start_pomodoros`: ポモドーロ自動開始
- `sound_enabled`: サウンド有効
- `sound_volume`: 音量（0-100）

### PomodoroSession（セッション履歴）
- `session_type`: "work", "break", "long_break"
- `duration`: 期間（分）
- `task_name`: タスク名（200文字以内）
- `notes`: メモ
- `completed`: 完了フラグ
- `started_at`: 開始時刻（ISO 8601形式）
- `ended_at`: 終了時刻（ISO 8601形式）

## フロントエンド統合例

```javascript
// 設定取得
async function getSettings() {
  const response = await fetch('http://localhost:5000/api/settings');
  const data = await response.json();
  return data.data;
}

// 設定更新
async function updateSettings(settings) {
  const response = await fetch('http://localhost:5000/api/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings)
  });
  const data = await response.json();
  return data.data;
}

// セッション保存
async function saveSession(session) {
  const response = await fetch('http://localhost:5000/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(session)
  });
  const data = await response.json();
  return data.data;
}

// 当日の履歴取得
async function getTodaySessions() {
  const today = new Date().toISOString().split('T')[0];
  const response = await fetch(`http://localhost:5000/api/sessions?date=${today}`);
  const data = await response.json();
  return data.data;
}
```
