# ポモドーロタイマー テスト容易性を高める設計改善案

## 1. Backend（Python）のテスト容易性改善

### 1.1 依存性注入（DI）の明確化 ✅ 重要度：高

#### 現状の課題
- サービス層が直接Repositoryインスタンスを生成すると、単体テストでモック化できない
- 外部依存（ファイルI/O、時刻取得）がハードコードされている

#### 改善案：コンストラクタインジェクション

```python
# services/settings_service.py
class SettingsService:
    def __init__(self, repository: SettingsRepositoryInterface):
        self._repository = repository
    
    def get_settings(self) -> SettingsModel:
        return self._repository.load()
    
    def update_settings(self, settings: SettingsModel) -> None:
        self._repository.save(settings)
```

#### テスト例
```python
# tests/test_settings_service.py
from unittest.mock import Mock

def test_get_settings_returns_repository_data():
    # Arrange
    mock_repo = Mock(spec=SettingsRepositoryInterface)
    mock_repo.load.return_value = SettingsModel(focus_duration=25)
    service = SettingsService(repository=mock_repo)
    
    # Act
    result = service.get_settings()
    
    # Assert
    assert result.focus_duration == 25
    mock_repo.load.assert_called_once()
```

---

### 1.2 時計の抽象化 ✅ 重要度：高

#### 現状の課題
```python
# 時刻依存のテストが不安定になる
def record_session(self):
    session = Session(
        completed_at=datetime.now()  # ❌ 直接呼び出し
    )
```

#### 改善案：Clockインターフェース

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
    """テスト用の固定時刻Clock"""
    def __init__(self, fixed_time: datetime):
        self._fixed_time = fixed_time
    
    def now(self) -> datetime:
        return self._fixed_time
```

#### テスト例
```python
# tests/test_session_service.py
def test_record_session_uses_provided_timestamp():
    # Arrange
    fixed_time = datetime(2026, 2, 24, 10, 30, 0)
    fake_clock = FakeClock(fixed_time)
    service = SessionService(
        repository=mock_repo,
        clock=fake_clock  # ✅ 固定時刻を注入
    )
    
    # Act
    session = service.record_completed_session(mode="focus")
    
    # Assert
    assert session.completed_at == fixed_time
```

---

### 1.3 Repository抽象化の強化 ✅ 重要度：高

#### 現状の課題
- インターフェースが未定義だと、実装への依存が発生する

#### 改善案：Protocol/ABCによる型定義

```python
# repositories/interfaces.py
from abc import ABC, abstractmethod
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

#### テスト用のFake実装

```python
# tests/fakes/fake_session_repository.py
class FakeSessionRepository:
    """テスト用のインメモリRepository"""
    
    def __init__(self):
        self._sessions: list[SessionModel] = []
    
    def save(self, session: SessionModel) -> None:
        self._sessions.append(session)
    
    def find_by_date(self, date: str) -> list[SessionModel]:
        return [s for s in self._sessions if s.date == date]
    
    def clear(self):
        """テスト間でのクリーンアップ用"""
        self._sessions.clear()
```

---

### 1.4 バリデーションの分離 ✅ 重要度：中

#### 現状の課題
```python
# routes.py 内でバリデーションを行うと、ルート層のテストが複雑化
@main_bp.put("/api/settings")
def update_settings():
    data = request.json
    if not data.get("focus_duration"):  # ❌ ルート層で検証
        return {"error": "..."}, 400
```

#### 改善案：バリデーション専用層

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
```

#### テスト例
```python
# tests/test_validators.py
def test_settings_validator_rejects_invalid_focus_duration():
    # Arrange
    invalid_data = {"focus_duration": 0}
    
    # Act
    errors = SettingsValidator.validate(invalid_data)
    
    # Assert
    assert len(errors) == 1
    assert errors[0].field == "focus_duration"
    assert errors[0].code == "OUT_OF_RANGE"
```

---

### 1.5 Flaskルートの薄層化 ✅ 重要度：高

#### 改善前（❌ 太いルート）
```python
@main_bp.put("/api/settings")
def update_settings():
    data = request.json
    
    # バリデーション（ルート層で実施）
    if not data.get("focus_duration"):
        return {"error": "..."}, 400
    
    # ビジネスロジック（ルート層で実施）
    settings = load_from_json()
    settings.update(data)
    save_to_json(settings)
    
    return {"status": "ok"}, 200
```

#### 改善後（✅ 薄いルート）
```python
@main_bp.put("/api/settings")
def update_settings():
    data = request.json
    
    # バリデーション → 専用層へ委譲
    errors = SettingsValidator.validate(data)
    if errors:
        return {"errors": [e.__dict__ for e in errors]}, 400
    
    # ビジネスロジック → サービス層へ委譲
    service = get_settings_service()
    service.update_settings(SettingsModel(**data))
    
    return {"status": "ok"}, 200
```

#### テストのメリット
- **ビジネスロジックのテスト**: サービス層を単独でテスト可能
- **ルート層のテスト**: I/Oの検証のみに集中できる

```python
# tests/test_routes.py（シンプルになる）
def test_update_settings_returns_400_on_invalid_input(client):
    response = client.put("/api/settings", json={"focus_duration": 0})
    assert response.status_code == 400
    assert "errors" in response.json
```

---

### 1.6 アプリケーションファクトリの拡張 ✅ 重要度：中

#### 現状
```python
# pomodoro/__init__.py
def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    if config:
        app.config.update(config)
    app.register_blueprint(main_bp)
    return app
```

#### 改善案：依存性を外部から注入可能に

```python
# pomodoro/__init__.py
def create_app(
    config: dict | None = None,
    settings_repository: SettingsRepositoryInterface | None = None,
    session_repository: SessionRepositoryInterface | None = None,
    clock: ClockInterface | None = None
) -> Flask:
    app = Flask(__name__)
    
    if config:
        app.config.update(config)
    
    # デフォルト実装を使用（本番環境）
    if settings_repository is None:
        settings_repository = JsonSettingsRepository("data/settings.json")
    if session_repository is None:
        session_repository = JsonSessionRepository("data/sessions.json")
    if clock is None:
        clock = SystemClock()
    
    # DIコンテナに登録（flask.gまたはapp.extensions経由）
    app.extensions["settings_repository"] = settings_repository
    app.extensions["session_repository"] = session_repository
    app.extensions["clock"] = clock
    
    app.register_blueprint(main_bp)
    return app
```

#### テストでの利用
```python
# tests/test_routes.py
def test_api_with_fake_dependencies():
    # Arrange
    fake_settings_repo = FakeSettingsRepository()
    fake_session_repo = FakeSessionRepository()
    fake_clock = FakeClock(datetime(2026, 2, 24, 10, 0, 0))
    
    app = create_app(
        config={"TESTING": True},
        settings_repository=fake_settings_repo,
        session_repository=fake_session_repo,
        clock=fake_clock
    )
    client = app.test_client()
    
    # Act & Assert
    response = client.get("/api/settings")
    assert response.status_code == 200
```

---

## 2. Frontend（JavaScript）のテスト容易性改善

### 2.1 純粋関数化の徹底 ✅ 重要度：高

#### 現状の課題
```javascript
// ❌ DOM依存のコード
function updateTimer() {
    const now = Date.now();
    const remaining = targetTime - now;
    document.querySelector('.time-display').textContent = formatTime(remaining);
}
```

#### 改善案：ロジックとDOM更新を分離

```javascript
// timer_engine.js（純粋関数）
export class TimerEngine {
    constructor(duration) {
        this.duration = duration;
        this.targetTime = null;
        this.state = 'idle';
    }
    
    start(currentTime) {
        this.targetTime = currentTime + this.duration * 1000;
        this.state = 'running';
    }
    
    getRemainingTime(currentTime) {
        if (this.state !== 'running') return this.duration * 1000;
        return Math.max(0, this.targetTime - currentTime);
    }
    
    isCompleted(currentTime) {
        return this.getRemainingTime(currentTime) === 0;
    }
}
```

#### テスト例（Jest/Vitest）
```javascript
// tests/timer_engine.test.js
import { TimerEngine } from '../timer_engine.js';

describe('TimerEngine', () => {
    test('計算が正しい残り時間を返す', () => {
        const engine = new TimerEngine(25 * 60); // 25分
        const startTime = 1000000;
        
        engine.start(startTime);
        
        const remaining = engine.getRemainingTime(startTime + 60000); // 1分後
        expect(remaining).toBe(24 * 60 * 1000); // 24分
    });
    
    test('完了判定が正しく動作する', () => {
        const engine = new TimerEngine(1); // 1秒
        const startTime = 1000000;
        
        engine.start(startTime);
        
        expect(engine.isCompleted(startTime + 999)).toBe(false);
        expect(engine.isCompleted(startTime + 1000)).toBe(true);
    });
});
```

---

### 2.2 DOM更新層の隔離 ✅ 重要度：高

#### 改善案：UI層は描画のみ担当

```javascript
// ui.js（DOM操作専用）
export class TimerUI {
    constructor(elements) {
        this.timeDisplay = elements.timeDisplay;
        this.progressRing = elements.progressRing;
        this.modeLabel = elements.modeLabel;
    }
    
    updateTimeDisplay(milliseconds) {
        const minutes = Math.floor(milliseconds / 60000);
        const seconds = Math.floor((milliseconds % 60000) / 1000);
        this.timeDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
    
    updateProgress(percentage) {
        const degrees = percentage * 360;
        this.progressRing.style.setProperty('--progress', `${degrees}deg`);
    }
    
    updateMode(mode) {
        const labels = {
            focus: '作業中',
            short_break: '短休憩',
            long_break: '長休憩'
        };
        this.modeLabel.textContent = labels[mode] || '';
    }
}
```

#### テスト例（DOM環境不要）
```javascript
// tests/ui.test.js
import { TimerUI } from '../ui.js';

describe('TimerUI', () => {
    test('時間表示が正しくフォーマットされる', () => {
        const mockElements = {
            timeDisplay: { textContent: '' },
            progressRing: { style: { setProperty: jest.fn() } },
            modeLabel: { textContent: '' }
        };
        const ui = new TimerUI(mockElements);
        
        ui.updateTimeDisplay(25 * 60 * 1000); // 25分
        
        expect(mockElements.timeDisplay.textContent).toBe('25:00');
    });
});
```

---

### 2.3 イベントハンドラの分離 ✅ 重要度：中

#### 改善案：app.jsは配線のみ

```javascript
// app.js（イベント配線）
import { TimerEngine } from './timer_engine.js';
import { TimerUI } from './ui.js';

class PomodoroApp {
    constructor(engine, ui) {
        this.engine = engine;
        this.ui = ui;
    }
    
    handleStartClick() {
        this.engine.start(Date.now());
        this.startTicking();
    }
    
    handleResetClick() {
        this.engine.reset();
        this.ui.updateTimeDisplay(this.engine.duration * 1000);
        this.ui.updateProgress(0);
    }
    
    startTicking() {
        this.intervalId = setInterval(() => {
            const remaining = this.engine.getRemainingTime(Date.now());
            this.ui.updateTimeDisplay(remaining);
            
            const progress = 1 - (remaining / (this.engine.duration * 1000));
            this.ui.updateProgress(progress);
            
            if (this.engine.isCompleted(Date.now())) {
                this.handleCompletion();
            }
        }, 100);
    }
    
    handleCompletion() {
        clearInterval(this.intervalId);
        // API呼び出し等
    }
}
```

---

### 2.4 API通信層の抽象化 ✅ 重要度：中

#### 改善案：APIクライアントを分離

```javascript
// api_client.js
export class PomodoroAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }
    
    async getSettings() {
        const response = await fetch(`${this.baseUrl}/api/settings`);
        if (!response.ok) throw new Error('Failed to fetch settings');
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
}
```

#### テスト用のFake実装
```javascript
// tests/fakes/fake_api.js
export class FakePomodoroAPI {
    constructor() {
        this.savedSessions = [];
        this.settings = { focus_duration: 25 };
    }
    
    async getSettings() {
        return this.settings;
    }
    
    async saveSession(session) {
        this.savedSessions.push(session);
        return { status: 'ok' };
    }
}
```

---

## 3. テスト構成の推奨構造

### 3.1 テストディレクトリ構造

```
tests/
├── unit/                      # 単体テスト
│   ├── domain/
│   │   ├── test_timer_state.py
│   │   └── test_validators.py
│   ├── services/
│   │   ├── test_settings_service.py
│   │   └── test_session_service.py
│   └── repositories/
│       ├── test_json_settings_repo.py
│       └── test_json_session_repo.py
├── integration/               # 統合テスト
│   ├── test_api_settings.py
│   └── test_api_sessions.py
├── e2e/                       # E2Eテスト（Playwright/Selenium）
│   └── test_timer_flow.py
├── fakes/                     # テスト用のFake実装
│   ├── fake_settings_repository.py
│   ├── fake_session_repository.py
│   └── fake_clock.py
└── fixtures/                  # テストデータ
    ├── settings.json
    └── sessions.json
```

---

### 3.2 テストユーティリティ

```python
# tests/conftest.py（pytest用）
import pytest
from datetime import datetime
from pomodoro import create_app
from tests.fakes.fake_settings_repository import FakeSettingsRepository
from tests.fakes.fake_session_repository import FakeSessionRepository
from tests.fakes.fake_clock import FakeClock

@pytest.fixture
def app():
    """テスト用のFlaskアプリ"""
    fake_settings_repo = FakeSettingsRepository()
    fake_session_repo = FakeSessionRepository()
    fake_clock = FakeClock(datetime(2026, 2, 24, 10, 0, 0))
    
    app = create_app(
        config={"TESTING": True},
        settings_repository=fake_settings_repo,
        session_repository=fake_session_repo,
        clock=fake_clock
    )
    yield app

@pytest.fixture
def client(app):
    """テスト用のHTTPクライアント"""
    return app.test_client()
```

---

## 4. テストカバレッジ戦略

### 4.1 優先度別テスト対象

| 優先度 | 対象 | テスト種別 |
|-------|------|----------|
| ⭐⭐⭐ | 状態遷移ロジック | 単体テスト |
| ⭐⭐⭐ | バリデーション | 単体テスト |
| ⭐⭐⭐ | タイマー計算ロジック | 単体テスト（JS） |
| ⭐⭐ | APIエンドポイント | 統合テスト |
| ⭐⭐ | サービス層 | 単体テスト |
| ⭐ | Repository実装 | 統合テスト |
| ⭐ | UI操作フロー | E2Eテスト |

---

### 4.2 テストカバレッジ目標

- **ドメイン層**: 90%以上
- **サービス層**: 85%以上
- **API層**: 80%以上
- **Repository層**: 70%以上（I/Oは統合テストで確認）

---

## 5. まとめ：テスト容易性を高める設計原則

### ✅ 実装すべき改善点（優先順位順）

1. **依存性注入の導入**（Repository、Clock）
2. **時計の抽象化**（時刻依存テストの安定化）
3. **Repository抽象化とFake実装**
4. **バリデーション層の分離**
5. **Flaskルートの薄層化**
6. **JavaScript純粋関数化**（timer_engine.js）
7. **DOM更新層の隔離**（ui.js）
8. **アプリケーションファクトリの拡張**

### 🎯 設計原則

1. **依存性逆転の原則（DIP）**: 高レベル層が低レベル層の抽象に依存
2. **単一責任の原則（SRP）**: 各モジュールは1つの責務のみ
3. **純粋関数の優先**: 副作用を持たない関数を多用
4. **外部依存の注入**: `datetime.now()`, `fetch()`などは抽象化
5. **テストピラミッドの遵守**: 単体テスト > 統合テスト > E2Eテスト

この設計により、**高速で安定したユニットテストが可能になり、リファクタリングやバグ修正の安全性が大幅に向上**します。
