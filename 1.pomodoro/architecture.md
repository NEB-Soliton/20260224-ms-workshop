# Pomodoro Webアプリ アーキテクチャ設計書

## 1. 目的と前提条件

### 1.1 プロジェクト概要
- Flask + HTML/CSS/JavaScriptを使用したポモドーロタイマーWebアプリケーション
- MVPの迅速な実装を優先し、将来的な機能拡張（履歴分析、認証、DB移行）に対応可能な設計
- 単一ページアプリケーション（SPA風）として実装

### 1.2 UI要件（モック準拠）
- **中央タイマー表示**: 残り時間（MM:SS形式）と円形プログレスバー
- **モード表示**: 現在の状態（作業中/短休憩/長休憩）
- **操作ボタン**: 開始/一時停止、リセット
- **進捗サマリー**: 今日の完了ポモドーロ数、累計集中時間

### 1.3 非機能要件
- **タイマー精度**: ドリフト抑制（`targetTimestamp - now` 方式）
- **テスト容易性**: 単体テストカバレッジ80%以上を目標
- **保守性**: 責務分離による変更容易性の確保
- **拡張性**: Repository パターンによる永続化層の差し替え対応

---

## 2. 全体アーキテクチャ

### 2.1 アーキテクチャ方針

#### フロントエンド主導のタイマー制御
- **JavaScript側の責務**
  - タイマーの開始・停止・一時停止・リセット
  - 残り時間の計算と表示更新（100msごと）
  - 円形プログレスバーのアニメーション制御
  
- **Flask側の責務**
  - 静的ファイル（HTML/CSS/JS）の配信
  - 設定の永続化API（作業時間、休憩時間など）
  - セッション履歴の保存・取得API

#### タイマー精度の確保
```javascript
// ❌ 秒の積算（ドリフトが発生）
remainingTime -= 1000;

// ✅ 目標時刻との差分計算（ドリフト抑制）
const remaining = targetTimestamp - Date.now();
```

### 2.2 レイヤ構成

```
┌─────────────────────────────────────────────┐
│  Presentation Layer                         │
│  - Flask Routes（薄いルート層）              │
│  - Template Rendering                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Application Service Layer                  │
│  - SettingsService                          │
│  - SessionService                           │
│  - ユースケース調停                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Domain Layer                               │
│  - TimerState（状態遷移ロジック）            │
│  - Validators（バリデーション）              │
│  - Models（データモデル）                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Infrastructure Layer                       │
│  - Repository Interfaces                    │
│  - JSON/SQLite Implementations              │
│  - Clock (時刻抽象化)                        │
└─────────────────────────────────────────────┘
```

### 2.3 責務の詳細

| レイヤ | 責務 | NG例 |
|-------|------|------|
| **Presentation** | HTTP入出力、ルーティング | ビジネスロジックの実装 |
| **Service** | ユースケース実装、調停 | 直接的なデータアクセス |
| **Domain** | ビジネスルール、状態遷移 | 外部依存の直接呼び出し |
| **Infrastructure** | 永続化、外部システム連携 | ビジネスロジックの実装 |

---

## 3. ドメインモデル設計

### 3.1 タイマー状態

```python
class TimerState(Enum):
    IDLE = "idle"           # 待機中
    RUNNING = "running"     # 実行中
    PAUSED = "paused"       # 一時停止
    COMPLETED = "completed" # 完了
```

### 3.2 タイマーモード

```python
class TimerMode(Enum):
    FOCUS = "focus"               # 作業（デフォルト25分）
    SHORT_BREAK = "short_break"   # 短休憩（デフォルト5分）
    LONG_BREAK = "long_break"     # 長休憩（デフォルト15分）
```

### 3.3 状態遷移ルール

```
┌──────┐  start   ┌─────────┐  pause   ┌────────┐
│ IDLE │ ───────→ │ RUNNING │ ───────→ │ PAUSED │
└──────┘          └─────────┘          └────────┘
   ↑                   │                    │
   │                   │ complete           │ resume
   │                   ↓                    ↓
   │              ┌───────────┐         ┌─────────┐
   └──────────────│ COMPLETED │         │ RUNNING │
        next      └───────────┘         └─────────┘
```

### 3.4 状態遷移の実装方針

```python
# domain/timer_state.py（純粋関数として実装）
def next_state(
    current_state: TimerState,
    event: str,
    context: dict
) -> tuple[TimerState, dict]:
    """
    状態遷移を計算する純粋関数
    
    Args:
        current_state: 現在の状態
        event: イベント（"start", "pause", "resume", "complete", "reset"）
        context: コンテキスト情報
    
    Returns:
        (新しい状態, 更新されたコンテキスト)
    """
    # 状態遷移ロジック（副作用なし）
    pass
```

**テスト容易性のポイント**:
- 純粋関数として実装（外部依存なし）
- すべての状態遷移パターンをユニットテストで網羅
- 無効な遷移は例外を発生させる

---

## 4. API設計

### 4.1 エンドポイント一覧

| メソッド | エンドポイント | 用途 | 認証 |
|---------|---------------|------|------|
| `GET` | `/` | HTML配信 | 不要 |
| `GET` | `/api/settings` | 設定取得 | 不要（将来は必要） |
| `PUT` | `/api/settings` | 設定更新 | 不要（将来は必要） |
| `POST` | `/api/sessions` | セッション記録 | 不要（将来は必要） |
| `GET` | `/api/sessions` | 履歴取得 | 不要（将来は必要） |

### 4.2 API仕様詳細

#### `GET /api/settings`

**レスポンス例**:
```json
{
  "focus_duration": 25,
  "short_break_duration": 5,
  "long_break_duration": 15,
  "long_break_interval": 4
}
```

#### `PUT /api/settings`

**リクエスト例**:
```json
{
  "focus_duration": 30,
  "short_break_duration": 5,
  "long_break_duration": 20,
  "long_break_interval": 4
}
```

**バリデーションルール**:
- `focus_duration`: 1〜60（分）
- `short_break_duration`: 1〜30（分）
- `long_break_duration`: 1〜60（分）
- `long_break_interval`: 1〜10（回）

**エラーレスポンス例**:
```json
{
  "errors": [
    {
      "field": "focus_duration",
      "code": "OUT_OF_RANGE",
      "message": "作業時間は1〜60分で指定してください"
    }
  ]
}
```

#### `POST /api/sessions`

**リクエスト例**:
```json
{
  "mode": "focus",
  "duration": 25,
  "completed_at": "2026-02-24T10:30:00Z"
}
```

**レスポンス例**:
```json
{
  "id": "session_123",
  "status": "recorded"
}
```

#### `GET /api/sessions?date=YYYY-MM-DD`

**レスポンス例**:
```json
{
  "date": "2026-02-24",
  "completed_count": 4,
  "total_focus_time": 100,
  "sessions": [
    {
      "id": "session_123",
      "mode": "focus",
      "duration": 25,
      "completed_at": "2026-02-24T10:30:00Z"
    }
  ]
}
```

### 4.3 エラーレスポンス統一規約

すべてのエラーは以下の形式で返却:

```json
{
  "errors": [
    {
      "field": "field_name",    // optional
      "code": "ERROR_CODE",
      "message": "人間が読めるメッセージ"
    }
  ]
}
```

**エラーコード一覧**:
- `VALIDATION_ERROR`: 入力値の検証エラー
- `OUT_OF_RANGE`: 値が許容範囲外
- `REQUIRED_FIELD`: 必須フィールドの欠落
- `INTERNAL_ERROR`: サーバー内部エラー

---

## 5. ディレクトリ構成

### 5.1 推奨構造

```text
/workspaces/20260224-ms-workshop/
├── architecture.md                    # 本ドキュメント
├── README.md
└── 1.pomodoro/
    ├── app.py                         # アプリケーションエントリポイント
    ├── features.md                    # 機能一覧
    ├── testing-architecture.md        # テスト設計詳細
    ├── pomodoro/
    │   ├── __init__.py                # create_app() ファクトリ
    │   ├── routes.py                  # ルート層（薄く保つ）
    │   │
    │   ├── domain/                    # ドメイン層
    │   │   ├── __init__.py
    │   │   ├── timer_state.py         # 状態遷移ロジック（純粋関数）
    │   │   ├── validators.py          # バリデーションロジック
    │   │   └── models.py              # データモデル
    │   │
    │   ├── services/                  # アプリケーションサービス層
    │   │   ├── __init__.py
    │   │   ├── settings_service.py    # 設定管理
    │   │   └── session_service.py     # セッション管理
    │   │
    │   ├── repositories/              # インフラストラクチャ層
    │   │   ├── __init__.py
    │   │   ├── interfaces.py          # Repository抽象（Protocol）
    │   │   ├── json_settings_repo.py  # JSON実装
    │   │   └── json_session_repo.py   # JSON実装
    │   │
    │   ├── infrastructure/            # その他インフラ
    │   │   ├── __init__.py
    │   │   └── clock.py               # 時刻抽象化
    │   │
    │   ├── templates/                 # HTMLテンプレート
    │   │   └── index.html
    │   │
    │   └── static/                    # 静的ファイル
    │       ├── css/
    │       │   └── style.css
    │       └── js/
    │           ├── app.js             # イベント配線・調停
    │           ├── timer_engine.js    # タイマーロジック（DOM非依存）
    │           └── ui.js              # DOM更新専用
    │
    ├── tests/                         # テストコード
    │   ├── __init__.py
    │   ├── conftest.py                # pytest設定・共通fixture
    │   │
    │   ├── unit/                      # 単体テスト
    │   │   ├── domain/
    │   │   │   ├── test_timer_state.py
    │   │   │   └── test_validators.py
    │   │   ├── services/
    │   │   │   ├── test_settings_service.py
    │   │   │   └── test_session_service.py
    │   │   └── repositories/
    │   │       └── test_json_repositories.py
    │   │
    │   ├── integration/               # 統合テスト
    │   │   ├── test_api_settings.py
    │   │   └── test_api_sessions.py
    │   │
    │   ├── fakes/                     # テスト用Fake実装
    │   │   ├── __init__.py
    │   │   ├── fake_settings_repository.py
    │   │   ├── fake_session_repository.py
    │   │   └── fake_clock.py
    │   │
    │   └── fixtures/                  # テストデータ
    │       ├── settings.json
    │       └── sessions.json
    │
    └── data/                          # 実行時データ（.gitignore対象）
        ├── settings.json
        └── sessions.json
```

### 5.2 各ディレクトリの責務

| ディレクトリ | 責務 | 依存方向 |
|-------------|------|---------|
| `domain/` | ビジネスルール、状態遷移 | 外部依存なし |
| `services/` | ユースケース実装 | domain → repositories |
| `repositories/` | データ永続化 | interfaces のみ公開 |
| `infrastructure/` | 外部システム抽象化 | - |
| `routes.py` | HTTP入出力 | services のみ呼び出し |
| `static/js/` | フロントエンドロジック | 階層分離（engine→ui→app） |

---

## 6. テスト容易性を高める設計原則

### 6.1 依存性注入（DI）の徹底

#### ❌ テストしにくい実装
```python
# services/settings_service.py
class SettingsService:
    def get_settings(self):
        # Repositoryを直接インスタンス化（モック不可）
        repo = JsonSettingsRepository("data/settings.json")
        return repo.load()
```

#### ✅ テストしやすい実装
```python
# services/settings_service.py
class SettingsService:
    def __init__(self, repository: SettingsRepositoryInterface):
        self._repository = repository  # コンストラクタ注入
    
    def get_settings(self) -> SettingsModel:
        return self._repository.load()

# tests/unit/services/test_settings_service.py
def test_get_settings():
    # Fake実装を注入可能
    fake_repo = FakeSettingsRepository()
    service = SettingsService(repository=fake_repo)
    
    result = service.get_settings()
    assert result.focus_duration == 25
```

### 6.2 時計の抽象化

#### 問題点
```python
from datetime import datetime

def record_session(self, mode: str):
    session = Session(
        mode=mode,
        completed_at=datetime.now()  # ❌ 直接呼び出し → 時刻依存テストが不安定
    )
```

#### 解決策: Clockインターフェース
```python
# infrastructure/clock.py
from abc import ABC, abstractmethod
from datetime import datetime

class ClockInterface(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass

class SystemClock(ClockInterface):
    """本番環境用"""
    def now(self) -> datetime:
        return datetime.now()

class FakeClock(ClockInterface):
    """テスト用（固定時刻）"""
    def __init__(self, fixed_time: datetime):
        self._fixed_time = fixed_time
    
    def now(self) -> datetime:
        return self._fixed_time

# 使用例
class SessionService:
    def __init__(self, repository, clock: ClockInterface):
        self._repository = repository
        self._clock = clock  # ✅ 注入可能
    
    def record_session(self, mode: str):
        session = Session(
            mode=mode,
            completed_at=self._clock.now()  # ✅ テストで固定可能
        )
        self._repository.save(session)
```

### 6.3 Repository抽象化

#### インターフェース定義
```python
# repositories/interfaces.py
from typing import Protocol
from pomodoro.domain.models import SettingsModel, SessionModel

class SettingsRepositoryInterface(Protocol):
    """設定の永続化インターフェース"""
    
    def load(self) -> SettingsModel:
        """現在の設定を取得"""
        ...
    
    def save(self, settings: SettingsModel) -> None:
        """設定を保存"""
        ...

class SessionRepositoryInterface(Protocol):
    """セッション履歴の永続化インターフェース"""
    
    def save(self, session: SessionModel) -> None:
        """セッションを記録"""
        ...
    
    def find_by_date(self, date: str) -> list[SessionModel]:
        """指定日のセッション一覧を取得"""
        ...
```

#### Fake実装（テスト用）
```python
# tests/fakes/fake_session_repository.py
class FakeSessionRepository:
    """インメモリRepository（テスト用）"""
    
    def __init__(self):
        self._sessions: list[SessionModel] = []
    
    def save(self, session: SessionModel) -> None:
        self._sessions.append(session)
    
    def find_by_date(self, date: str) -> list[SessionModel]:
        return [s for s in self._sessions if s.date == date]
    
    def clear(self):
        """テスト間のクリーンアップ"""
        self._sessions.clear()
```

### 6.4 バリデーション層の分離

#### ルート層での検証（❌ アンチパターン）
```python
@main_bp.put("/api/settings")
def update_settings():
    data = request.json
    # ルート層でバリデーション → テストが困難
    if not data.get("focus_duration") or data["focus_duration"] < 1:
        return {"error": "..."}, 400
```

#### 専用層への分離（✅ ベストプラクティス）
```python
# domain/validators.py
from dataclasses import dataclass

@dataclass
class ValidationError:
    field: str
    code: str
    message: str

class SettingsValidator:
    @staticmethod
    def validate(data: dict) -> list[ValidationError]:
        errors = []
        
        focus = data.get("focus_duration")
        if not focus or not (1 <= focus <= 60):
            errors.append(ValidationError(
                field="focus_duration",
                code="OUT_OF_RANGE",
                message="作業時間は1〜60分で指定してください"
            ))
        
        return errors

# routes.py（薄いルート）
@main_bp.put("/api/settings")
def update_settings():
    data = request.json
    errors = SettingsValidator.validate(data)  # ✅ 分離された検証
    if errors:
        return {"errors": [e.__dict__ for e in errors]}, 400
    
    service = get_settings_service()
    service.update_settings(SettingsModel(**data))
    return {"status": "ok"}, 200
```

### 6.5 アプリケーションファクトリの拡張

#### 依存性を外部から注入可能に
```python
# pomodoro/__init__.py
from flask import Flask
from .routes import main_bp
from .repositories.interfaces import SettingsRepositoryInterface, SessionRepositoryInterface
from .infrastructure.clock import ClockInterface, SystemClock

def create_app(
    config: dict | None = None,
    settings_repository: SettingsRepositoryInterface | None = None,
    session_repository: SessionRepositoryInterface | None = None,
    clock: ClockInterface | None = None
) -> Flask:
    """
    Flaskアプリケーションファクトリ
    
    Args:
        config: アプリケーション設定
        settings_repository: 設定Repository（テスト時はFake注入）
        session_repository: セッションRepository（テスト時はFake注入）
        clock: 時刻提供（テスト時はFakeClock注入）
    """
    app = Flask(__name__)
    
    if config:
        app.config.update(config)
    
    # デフォルト実装（本番環境）
    if settings_repository is None:
        from .repositories.json_settings_repo import JsonSettingsRepository
        settings_repository = JsonSettingsRepository("data/settings.json")
    
    if session_repository is None:
        from .repositories.json_session_repo import JsonSessionRepository
        session_repository = JsonSessionRepository("data/sessions.json")
    
    if clock is None:
        clock = SystemClock()
    
    # DIコンテナに登録
    app.extensions["settings_repository"] = settings_repository
    app.extensions["session_repository"] = session_repository
    app.extensions["clock"] = clock
    
    app.register_blueprint(main_bp)
    return app
```

#### テストでの利用
```python
# tests/conftest.py
import pytest
from datetime import datetime
from pomodoro import create_app
from tests.fakes.fake_settings_repository import FakeSettingsRepository
from tests.fakes.fake_session_repository import FakeSessionRepository
from tests.fakes.fake_clock import FakeClock

@pytest.fixture
def app():
    """テスト用アプリケーション"""
    fake_clock = FakeClock(datetime(2026, 2, 24, 10, 0, 0))
    
    app = create_app(
        config={"TESTING": True},
        settings_repository=FakeSettingsRepository(),
        session_repository=FakeSessionRepository(),
        clock=fake_clock  # ✅ 固定時刻で実行
    )
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
```

---

## 7. フロントエンドアーキテクチャ

### 7.1 3層分離の原則

| ファイル | 責務 | 依存関係 | テスト方法 |
|---------|------|---------|-----------|
| `timer_engine.js` | タイマー計算ロジック<br>状態管理（純粋関数） | **DOM依存なし** | Jest/Vitest（高速） |
| `ui.js` | DOM更新専用<br>描画処理 | timer_engine.js | モックDOM |
| `app.js` | イベント配線<br>API連携 | ui.js, timer_engine.js | E2Eテスト |

### 7.2 timer_engine.js（ロジック層）

```javascript
/**
 * タイマーエンジン（純粋ロジック、DOM非依存）
 */
export class TimerEngine {
    constructor(durationMinutes) {
        this.duration = durationMinutes * 60 * 1000; // ミリ秒
        this.targetTime = null;
        this.state = 'idle';
        this.mode = 'focus';
    }
    
    /**
     * タイマーを開始（現在時刻を受け取る）
     */
    start(currentTime) {
        this.targetTime = currentTime + this.duration;
        this.state = 'running';
    }
    
    /**
     * 残り時間を計算（ドリフト抑制）
     */
    getRemainingTime(currentTime) {
        if (this.state !== 'running') {
            return this.duration;
        }
        return Math.max(0, this.targetTime - currentTime);
    }
    
    /**
     * 完了判定
     */
    isCompleted(currentTime) {
        return this.state === 'running' && this.getRemainingTime(currentTime) === 0;
    }
    
    /**
     * 一時停止
     */
    pause(currentTime) {
        if (this.state === 'running') {
            this.duration = this.getRemainingTime(currentTime);
            this.state = 'paused';
        }
    }
    
    /**
     * 再開
     */
    resume(currentTime) {
        if (this.state === 'paused') {
            this.start(currentTime);
        }
    }
    
    /**
     * リセット
     */
    reset(originalDuration) {
        this.duration = originalDuration * 60 * 1000;
        this.targetTime = null;
        this.state = 'idle';
    }
}
```

**テスト例**:
```javascript
// tests/timer_engine.test.js
import { TimerEngine } from '../timer_engine.js';

describe('TimerEngine', () => {
    test('正しい残り時間を返す', () => {
        const engine = new TimerEngine(25);
        const startTime = 1000000;
        
        engine.start(startTime);
        
        const remaining = engine.getRemainingTime(startTime + 60000); // 1分後
        expect(remaining).toBe(24 * 60 * 1000); // 24分残り
    });
    
    test('完了判定が正しく動作', () => {
        const engine = new TimerEngine(1/60); // 1秒
        const startTime = 1000000;
        
        engine.start(startTime);
        
        expect(engine.isCompleted(startTime + 999)).toBe(false);
        expect(engine.isCompleted(startTime + 1000)).toBe(true);
    });
});
```

### 7.3 ui.js（描画層）

```javascript
/**
 * UI更新専用クラス（DOM操作のみ）
 */
export class TimerUI {
    constructor(elements) {
        this.timeDisplay = elements.timeDisplay;
        this.progressRing = elements.progressRing;
        this.modeLabel = elements.modeLabel;
        this.startButton = elements.startButton;
        this.resetButton = elements.resetButton;
    }
    
    /**
     * 時間表示を更新
     */
    updateTimeDisplay(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        this.timeDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
    
    /**
     * 円形プログレスを更新
     */
    updateProgress(percentage) {
        const degrees = percentage * 360;
        this.progressRing.style.setProperty('--progress', `${degrees}deg`);
    }
    
    /**
     * モードラベルを更新
     */
    updateMode(mode) {
        const labels = {
            focus: '作業中',
            short_break: '短休憩',
            long_break: '長休憩'
        };
        this.modeLabel.textContent = labels[mode] || '';
    }
    
    /**
     * ボタンテキストを更新
     */
    updateButton(state) {
        const buttonTexts = {
            idle: '開始',
            running: '一時停止',
            paused: '再開',
            completed: '開始'
        };
        this.startButton.textContent = buttonTexts[state] || '開始';
    }
    
    /**
     * 進捗サマリーを更新
     */
    updateSummary(completedCount, totalMinutes) {
        document.querySelector('.summary-value').textContent = completedCount;
        document.querySelector('.summary-value:nth-of-type(2)').textContent = 
            `${Math.floor(totalMinutes / 60)}時間${totalMinutes % 60}分`;
    }
}
```

### 7.4 app.js（調停層）

```javascript
/**
 * アプリケーションメインクラス（イベント配線・調停）
 */
import { TimerEngine } from './timer_engine.js';
import { TimerUI } from './ui.js';

class PomodoroApp {
    constructor(engine, ui, api) {
        this.engine = engine;
        this.ui = ui;
        this.api = api;
        this.intervalId = null;
    }
    
    /**
     * 初期化
     */
    async init() {
        // 設定を読み込み
        const settings = await this.api.getSettings();
        this.engine = new TimerEngine(settings.focus_duration);
        
        // イベントリスナー設定
        this.ui.startButton.addEventListener('click', () => this.handleStartClick());
        this.ui.resetButton.addEventListener('click', () => this.handleResetClick());
        
        // 今日の進捗を読み込み
        await this.loadTodaysSummary();
    }
    
    /**
     * 開始ボタンクリック
     */
    handleStartClick() {
        if (this.engine.state === 'idle' || this.engine.state === 'paused') {
            this.engine.state === 'idle' 
                ? this.engine.start(Date.now())
                : this.engine.resume(Date.now());
            this.startTicking();
        } else if (this.engine.state === 'running') {
            this.engine.pause(Date.now());
            this.stopTicking();
        }
        this.ui.updateButton(this.engine.state);
    }
    
    /**
     * リセットボタンクリック
     */
    handleResetClick() {
        this.stopTicking();
        this.engine.reset(25);
        this.ui.updateTimeDisplay(this.engine.duration);
        this.ui.updateProgress(0);
        this.ui.updateButton('idle');
    }
    
    /**
     * タイマー更新ループ
     */
    startTicking() {
        this.intervalId = setInterval(() => {
            const remaining = this.engine.getRemainingTime(Date.now());
            this.ui.updateTimeDisplay(remaining);
            
            const progress = 1 - (remaining / this.engine.duration);
            this.ui.updateProgress(progress);
            
            if (this.engine.isCompleted(Date.now())) {
                this.handleCompletion();
            }
        }, 100); // 100msごとに更新
    }
    
    /**
     * タイマー停止
     */
    stopTicking() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    
    /**
     * 完了処理
     */
    async handleCompletion() {
        this.stopTicking();
        this.engine.state = 'completed';
        
        // セッション記録
        await this.api.saveSession({
            mode: this.engine.mode,
            duration: this.engine.duration / 60000,
            completed_at: new Date().toISOString()
        });
        
        // 進捗更新
        await this.loadTodaysSummary();
        
        // 音声通知（将来実装）
        // this.playNotification();
    }
    
    /**
     * 今日の進捗を読み込み
     */
    async loadTodaysSummary() {
        const today = new Date().toISOString().split('T')[0];
        const summary = await this.api.getSessions(today);
        this.ui.updateSummary(summary.completed_count, summary.total_focus_time);
    }
}

// アプリケーション起動
document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        timeDisplay: document.querySelector('.time-display'),
        progressRing: document.querySelector('.progress-ring'),
        modeLabel: document.querySelector('.mode-label'),
        startButton: document.querySelector('.btn-primary'),
        resetButton: document.querySelector('.btn-outline')
    };
    
    const ui = new TimerUI(elements);
    const api = new PomodoroAPI();
    const engine = new TimerEngine(25);
    const app = new PomodoroApp(engine, ui, api);
    
    app.init();
});
```

### 7.5 API通信層の抽象化

```javascript
/**
 * API通信クライアント
 */
export class PomodoroAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }
    
    async getSettings() {
        const response = await fetch(`${this.baseUrl}/api/settings`);
        if (!response.ok) throw new Error('Failed to fetch settings');
        return response.json();
    }
    
    async updateSettings(settings) {
        const response = await fetch(`${this.baseUrl}/api/settings`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        if (!response.ok) throw new Error('Failed to update settings');
        return response.json();
    }
    
    async saveSession(session) {
        const response = await fetch(`${this.baseUrl}/api/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(session)
        });
        if (!response.ok) throw new Error('Failed to save session');
        return response.json();
    }
    
    async getSessions(date) {
        const response = await fetch(`${this.baseUrl}/api/sessions?date=${date}`);
        if (!response.ok) throw new Error('Failed to fetch sessions');
        return response.json();
    }
}
```

---

## 8. 実装ステップ（推奨順序）

### Phase 1: 静的UI実装 ✅ 完了
- [x] HTML構造作成（index.html）
- [x] CSSスタイリング（style.css）
- [x] 円形プログレスバーのデザイン
- [x] レスポンシブ対応

### Phase 2: フロントエンドロジック実装
1. **timer_engine.js 実装**
   - [ ] TimerEngineクラスの実装
   - [ ] 状態管理ロジック
   - [ ] 残り時間計算（ドリフト抑制）
   - [ ] ユニットテスト作成

2. **ui.js 実装**
   - [ ] TimerUIクラスの実装
   - [ ] DOM更新メソッド
   - [ ] 円形プログレスの描画ロジック
   - [ ] モック環境でのテスト

3. **app.js 実装**
   - [ ] PomodoroAppクラスの実装
   - [ ] イベントハンドラ配線
   - [ ] タイマー更新ループ
   - [ ] 完了時の処理

### Phase 3: バックエンドAPI実装
1. **ドメイン層**
   - [ ] models.py（データモデル定義）
   - [ ] validators.py（バリデーション）
   - [ ] timer_state.py（状態遷移ロジック）
   - [ ] ユニットテスト作成

2. **インフラ層**
   - [ ] clock.py（時刻抽象化）
   - [ ] interfaces.py（Repository抽象定義）
   - [ ] json_settings_repo.py（JSON実装）
   - [ ] json_session_repo.py（JSON実装）

3. **サービス層**
   - [ ] settings_service.py
   - [ ] session_service.py
   - [ ] ユニットテスト作成

4. **ルート層**
   - [ ] `GET /api/settings`
   - [ ] `PUT /api/settings`
   - [ ] `POST /api/sessions`
   - [ ] `GET /api/sessions`
   - [ ] 統合テスト作成

### Phase 4: フロント・バックエンド連携
- [ ] API通信クライアント実装（api_client.js）
- [ ] 設定の読み込み・保存
- [ ] セッション記録の自動化
- [ ] 進捗表示の動的更新
- [ ] E2Eテスト作成

### Phase 5: 改善・最適化
- [ ] エラーハンドリング強化
- [ ] ローディング表示
- [ ] 通知機能（音・ブラウザ通知）
- [ ] パフォーマンス最適化
- [ ] テストカバレッジ確認

---

## 9. テスト戦略

### 9.1 テストピラミッド

```
        ┌────────┐
        │  E2E   │  数個（重要フローのみ）
        └────────┘
       ┌──────────┐
       │ 統合テスト │  10-20個（API契約）
       └──────────┘
      ┌─────────────┐
      │ 単体テスト   │  50-100個（ロジック網羅）
      └─────────────┘
```

### 9.2 テストカバレッジ目標

| レイヤ | 目標カバレッジ | 重点テスト項目 |
|-------|--------------|--------------|
| **Domain** | 90%以上 | 状態遷移、バリデーション、境界値 |
| **Services** | 85%以上 | ビジネスロジック、エラーハンドリング |
| **Routes** | 80%以上 | API契約、ステータスコード、エラー形式 |
| **Repository** | 70%以上 | 統合テストで確認（I/O含む） |
| **JavaScript** | 80%以上 | timer_engine, ui（純粋関数優先） |

### 9.3 テストツール

| 用途 | ツール | 理由 |
|-----|--------|------|
| **Python単体テスト** | pytest | Fixture、パラメトライズが強力 |
| **Python統合テスト** | pytest + Flask test_client | APIテストが容易 |
| **JavaScriptテスト** | Jest / Vitest | モダンで高速 |
| **E2Eテスト** | Playwright / Selenium | ブラウザ自動化 |
| **カバレッジ** | pytest-cov / c8 | レポート生成 |

### 9.4 テスト実行コマンド

```bash
# Python単体テスト
pytest tests/unit/ -v

# Python統合テスト
pytest tests/integration/ -v

# すべてのPythonテスト（カバレッジ付き）
pytest tests/ --cov=pomodoro --cov-report=html

# JavaScriptテスト
npm test

# E2Eテスト
pytest tests/e2e/ --headed
```

### 9.5 継続的インテグレーション

```yaml
# .github/workflows/test.yml（例）
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=pomodoro --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 10. 技術選定の理由

### 10.1 バックエンド

| 技術 | 選定理由 |
|-----|---------|
| **Flask** | 軽量、学習コストが低い、MVPに最適 |
| **JSON永続化** | 初期実装が高速、後でSQLiteへ移行可能 |
| **Protocol型ヒント** | Repository抽象化が型安全 |
| **pytest** | Fixture、パラメトライズが強力 |

### 10.2 フロントエンド

| 技術 | 選定理由 |
|-----|---------|
| **Vanilla JS** | フレームワーク不要、シンプル、学習コスト低 |
| **CSS conic-gradient** | 円形プログレスがライブラリ不要で実装可能 |
| **Fetch API** | モダンなHTTP通信、Promise対応 |

### 10.3 タイマー精度の技術選択

| 方式 | メリット | デメリット | 採用 |
|-----|---------|-----------|------|
| 秒の積算 | シンプル | ドリフト発生 | ❌ |
| targetTime - now | 精度高い | 少し複雑 | ✅ |
| Web Workers | バックグラウンド動作 | オーバースペック | 将来検討 |

---

## 11. 将来拡張ポイント

### 11.1 データ永続化の進化

```
Phase 1: JSON（現在）
   ↓
Phase 2: SQLite（ローカル）
   ↓
Phase 3: PostgreSQL/MySQL（マルチユーザー）
```

**Repository差し替えで対応可能**（インターフェース不変）

### 11.2 機能拡張候補

| 機能 | 優先度 | 影響範囲 |
|-----|-------|---------|
| **音声通知** | 高 | フロントエンド（ui.js） |
| **ブラウザ通知** | 高 | フロントエンド（Notification API） |
| **自動モード切替** | 中 | timer_engine.js, app.js |
| **設定画面UI** | 中 | 新規HTML + API連携 |
| **週次/月次グラフ** | 中 | 新規ページ + D3.js |
| **ユーザー認証** | 低 | 全体（Flask-Login導入） |
| **PWA対応** | 低 | Service Worker追加 |
| **ダークモード** | 低 | CSS変数の追加 |

### 11.3 スケーラビリティ

#### シングルユーザー → マルチユーザー対応

1. **認証追加**（Flask-Login, JWT）
2. **DB移行**（SQLite → PostgreSQL）
3. **ユーザーIDをセッションに紐付け**
4. **Repository実装の差し替え**（既存コード変更最小）

#### パフォーマンス最適化

- **キャッシング**: Redis導入（セッション、設定）
- **API最適化**: GraphQL検討（複数エンドポイントの統合）
- **フロントエンド**: 仮想DOM導入（React/Vue）の検討

---

## 12. セキュリティ考慮事項

### 12.1 現在のMVP

- [ ] XSS対策（Flaskのテンプレートエスケープ）
- [ ] CSRF対策（Flask-WTF導入検討）
- [ ] 入力値サニタイゼーション（validators.pyで実装）

### 12.2 将来の認証実装時

- [ ] パスワードハッシュ化（bcrypt, Argon2）
- [ ] セッション管理（HTTPOnly Cookie）
- [ ] レート制限（Flask-Limiter）
- [ ] HTTPS強制（本番環境）

---

## 13. 開発環境とツール

### 13.1 推奨開発環境

```bash
# Python環境
python 3.11+
pip install flask pytest pytest-cov

# JavaScript環境（オプション）
node 18+
npm install --save-dev jest @testing-library/dom

# エディタ
VS Code + 拡張機能:
  - Python (pylance)
  - Prettier
  - ESLint
```

### 13.2 コード品質ツール

```bash
# Python
black pomodoro/            # コードフォーマット
flake8 pomodoro/           # リント
mypy pomodoro/             # 型チェック

# JavaScript
prettier --write static/js/  # コードフォーマット
eslint static/js/            # リント
```

---

## 14. まとめ

### 14.1 アーキテクチャの特徴

✅ **テスト容易性**: DI、Clock抽象化、Repository抽象化による高いテスタビリティ  
✅ **保守性**: 責務分離（レイヤ化）による変更容易性  
✅ **拡張性**: Repository差し替えでDB移行可能  
✅ **シンプルさ**: MVPに必要な機能に絞り込み、過度な抽象化を避ける  

### 14.2 次のアクション

1. **Phase 2（フロントエンドロジック）** の実装開始
   - timer_engine.js から着手（最も重要）
   - ユニットテストを先に書く（TDD推奨）

2. **Phase 3（バックエンドAPI）** の実装
   - ドメイン層から着手（外部依存なし）
   - Repository Fake実装も同時作成

3. **Phase 4（連携）** でMVP完成
   - フロント・バックエンド統合
   - E2Eテストで動作確認

この設計により、**高品質なコード、高速な開発サイクル、将来の機能追加への対応力**を同時に実現できます。

---

## 付録: 参考リンク

- [Flask公式ドキュメント](https://flask.palletsprojects.com/)
- [pytest公式ドキュメント](https://docs.pytest.org/)
- [Testing Best Practices](https://testdriven.io/)