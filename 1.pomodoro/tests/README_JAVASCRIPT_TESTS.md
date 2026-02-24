# JavaScript Tests for Timer Engine

JavaScript のタイマーエンジンの状態遷移テストを実装するには、Jest または Mocha/Chai を使用します。

## テスト実装手順

### 1. Node.js テスト環境のセットアップ

```bash
cd 1.pomodoro
npm init -y
npm install --save-dev jest @types/jest
```

### 2. package.json の設定

```json
{
  "scripts": {
    "test": "pytest tests/",
    "test:js": "jest static/js/__tests__",
    "test:all": "npm run test && npm run test:js"
  },
  "jest": {
    "testEnvironment": "jsdom",
    "testMatch": ["**/__tests__/**/*.test.js"]
  }
}
```

### 3. テストファイルの作成

`static/js/__tests__/timer_engine.test.js` を作成:

```javascript
/**
 * Timer Engine State Transition Tests
 * タイマーエンジンの状態遷移テスト
 */

// Load the timer engine
const fs = require('fs');
const path = require('path');
const timerEngineCode = fs.readFileSync(
    path.join(__dirname, '../timer_engine.js'),
    'utf8'
);

// Create a mock window object
global.window = {};

// Execute the timer engine code
eval(timerEngineCode);

const { TimerEngine, TimerState, TimerMode } = global.window;

describe('TimerEngine', () => {
    let timer;

    beforeEach(() => {
        timer = new TimerEngine(25, 5);
        jest.useFakeTimers();
    });

    afterEach(() => {
        if (timer.intervalId) {
            clearInterval(timer.intervalId);
        }
        jest.clearAllTimers();
    });

    describe('初期状態', () => {
        test('初期状態はIDLE', () => {
            expect(timer.state).toBe(TimerState.IDLE);
        });

        test('初期モードはWORK', () => {
            expect(timer.mode).toBe(TimerMode.WORK);
        });

        test('初期残り時間は作業時間', () => {
            expect(timer.remainingTime).toBe(25 * 60);
        });
    });

    describe('start() - 開始', () => {
        test('IDLEからRUNNINGに遷移', () => {
            const result = timer.start();
            expect(result).toBe(true);
            expect(timer.state).toBe(TimerState.RUNNING);
        });

        test('targetTimestampが設定される', () => {
            timer.start();
            expect(timer.targetTimestamp).not.toBeNull();
            expect(timer.targetTimestamp).toBeGreaterThan(Date.now());
        });

        test('既にRUNNING状態では開始できない', () => {
            timer.start();
            const result = timer.start();
            expect(result).toBe(false);
        });
    });

    describe('pause() - 一時停止', () => {
        test('RUNNINGからPAUSEDに遷移', () => {
            timer.start();
            const result = timer.pause();
            expect(result).toBe(true);
            expect(timer.state).toBe(TimerState.PAUSED);
        });

        test('IDLE状態では一時停止できない', () => {
            const result = timer.pause();
            expect(result).toBe(false);
        });

        test('一時停止後、残り時間が保持される', () => {
            timer.start();
            jest.advanceTimersByTime(5000); // 5秒経過
            timer.pause();
            
            const remaining = timer.getRemainingTime();
            expect(remaining).toBeLessThan(25 * 60);
            expect(remaining).toBeGreaterThan(24 * 60);
        });
    });

    describe('resume() - 再開', () => {
        test('PAUSEDからRUNNINGに遷移', () => {
            timer.start();
            timer.pause();
            const result = timer.resume();
            expect(result).toBe(true);
            expect(timer.state).toBe(TimerState.RUNNING);
        });

        test('IDLE状態では再開できない', () => {
            const result = timer.resume();
            expect(result).toBe(false);
        });
    });

    describe('reset() - リセット', () => {
        test('任意の状態からIDLEに遷移', () => {
            timer.start();
            timer.reset();
            expect(timer.state).toBe(TimerState.IDLE);
        });

        test('残り時間がリセットされる', () => {
            timer.start();
            jest.advanceTimersByTime(5000);
            timer.reset();
            expect(timer.remainingTime).toBe(25 * 60);
        });

        test('targetTimestampがnullになる', () => {
            timer.start();
            timer.reset();
            expect(timer.targetTimestamp).toBeNull();
        });
    });

    describe('switchMode() - モード切替', () => {
        test('WORKからBREAKに切り替わる', () => {
            timer.switchMode();
            expect(timer.mode).toBe(TimerMode.BREAK);
        });

        test('BREAKからWORKに切り替わる', () => {
            timer.switchMode();
            timer.switchMode();
            expect(timer.mode).toBe(TimerMode.WORK);
        });

        test('モード切替後、残り時間が更新される', () => {
            timer.switchMode(); // BREAK mode
            expect(timer.remainingTime).toBe(5 * 60);
        });

        test('モード切替後、状態がIDLEになる', () => {
            timer.start();
            timer.switchMode();
            expect(timer.state).toBe(TimerState.IDLE);
        });
    });

    describe('getRemainingTime() - 残り時間取得', () => {
        test('IDLE状態で正しい残り時間を返す', () => {
            const remaining = timer.getRemainingTime();
            expect(remaining).toBe(25 * 60);
        });

        test('RUNNING状態で経過時間を反映', () => {
            timer.start();
            jest.advanceTimersByTime(10000); // 10秒経過
            
            const remaining = timer.getRemainingTime();
            expect(remaining).toBeLessThan(25 * 60);
            expect(remaining).toBeGreaterThan(24 * 60);
        });

        test('負の値にならない', () => {
            timer.start();
            jest.advanceTimersByTime(30 * 60 * 1000); // 30分経過
            
            const remaining = timer.getRemainingTime();
            expect(remaining).toBeGreaterThanOrEqual(0);
        });
    });

    describe('getProgress() - 進捗取得', () => {
        test('開始時は0', () => {
            const progress = timer.getProgress();
            expect(progress).toBe(0);
        });

        test('半分経過で0.5前後', () => {
            timer.start();
            jest.advanceTimersByTime(12.5 * 60 * 1000); // 12.5分経過
            
            const progress = timer.getProgress();
            expect(progress).toBeGreaterThan(0.4);
            expect(progress).toBeLessThan(0.6);
        });

        test('完了時は1.0', () => {
            timer.start();
            jest.advanceTimersByTime(25 * 60 * 1000); // 25分経過
            
            const progress = timer.getProgress();
            expect(progress).toBeCloseTo(1.0, 1);
        });
    });

    describe('getState() - 状態取得', () => {
        test('状態情報を含むオブジェクトを返す', () => {
            const state = timer.getState();
            
            expect(state).toHaveProperty('state');
            expect(state).toHaveProperty('mode');
            expect(state).toHaveProperty('remainingTime');
            expect(state).toHaveProperty('progress');
            expect(state).toHaveProperty('isRunning');
            expect(state).toHaveProperty('isPaused');
            expect(state).toHaveProperty('isIdle');
        });

        test('IDLE状態のフラグが正しい', () => {
            const state = timer.getState();
            expect(state.isIdle).toBe(true);
            expect(state.isRunning).toBe(false);
            expect(state.isPaused).toBe(false);
        });

        test('RUNNING状態のフラグが正しい', () => {
            timer.start();
            const state = timer.getState();
            expect(state.isIdle).toBe(false);
            expect(state.isRunning).toBe(true);
            expect(state.isPaused).toBe(false);
        });
    });

    describe('コールバック', () => {
        test('onTickが呼ばれる', () => {
            const mockTick = jest.fn();
            timer.onTick = mockTick;
            
            timer.start();
            jest.advanceTimersByTime(200);
            
            expect(mockTick).toHaveBeenCalled();
        });

        test('onCompleteが完了時に呼ばれる', () => {
            const mockComplete = jest.fn();
            timer.onComplete = mockComplete;
            
            timer.start();
            jest.advanceTimersByTime(25 * 60 * 1000 + 1000);
            
            expect(mockComplete).toHaveBeenCalled();
        });

        test('onStateChangeが状態変化時に呼ばれる', () => {
            const mockStateChange = jest.fn();
            timer.onStateChange = mockStateChange;
            
            timer.start();
            expect(mockStateChange).toHaveBeenCalled();
            
            timer.pause();
            expect(mockStateChange).toHaveBeenCalledTimes(2);
        });
    });

    describe('設定変更', () => {
        test('setWorkDuration()で作業時間を変更', () => {
            timer.setWorkDuration(30);
            expect(timer.workDuration).toBe(30 * 60);
            expect(timer.remainingTime).toBe(30 * 60);
        });

        test('setBreakDuration()で休憩時間を変更', () => {
            timer.setBreakDuration(10);
            expect(timer.breakDuration).toBe(10 * 60);
        });
    });

    describe('エッジケース', () => {
        test('0秒で完了する', () => {
            timer.remainingTime = 0;
            timer.start();
            jest.advanceTimersByTime(200);
            
            expect(timer.state).toBe(TimerState.COMPLETED);
        });

        test('連続してstartを呼んでも問題ない', () => {
            timer.start();
            timer.start();
            timer.start();
            expect(timer.state).toBe(TimerState.RUNNING);
        });

        test('pause/resumeを繰り返しても正常動作', () => {
            timer.start();
            timer.pause();
            timer.resume();
            timer.pause();
            timer.resume();
            expect(timer.state).toBe(TimerState.RUNNING);
        });
    });
});
```

## テスト実行

```bash
# Python tests
pytest tests/ -v --cov=pomodoro --cov-report=html

# JavaScript tests (Jest をインストールした後)
npm test:js

# All tests
npm test:all
```

## 注意事項

1. JavaScript テストは Node.js 環境が必要です
2. `jsdom` を使用してブラウザ環境をシミュレートします
3. タイマーの時間経過は `jest.useFakeTimers()` でモックします
4. 実際のプロジェクトでは、Jest の設定を追加して実行してください

## カバレッジ目標

- 状態遷移ロジック: 100%
- エッジケース: 主要パターンをカバー
- コールバック機能: 全パターンをテスト
