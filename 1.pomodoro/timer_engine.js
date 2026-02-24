/**
 * タイマーエンジン - コアロジックと状態管理
 */
(function(window) {
    'use strict';

    // 定数
    const WORK_DURATION = 25 * 60; // 25分（秒単位）
    const BREAK_DURATION = 5 * 60; // 5分（秒単位）

    // タイマーの状態
    const TimerState = {
        IDLE: 'idle',
        RUNNING: 'running',
        PAUSED: 'paused',
        COMPLETED: 'completed'
    };

    // モード
    const TimerMode = {
        WORK: 'work',
        BREAK: 'break'
    };

    /**
     * タイマーエンジンクラス
     */
    class TimerEngine {
        constructor() {
            this.state = TimerState.IDLE;
            this.mode = TimerMode.WORK;
            this.remainingTime = WORK_DURATION;
            this.totalTime = WORK_DURATION;
            this.intervalId = null;
            this.listeners = {
                tick: [],
                stateChange: [],
                modeChange: [],
                complete: []
            };
            
            // 今日の進捗データ
            this.todayStats = {
                completed: 0,
                focusTimeMinutes: 0
            };
            
            // localStorage から進捗を読み込み
            this.loadTodayStats();
        }

        /**
         * イベントリスナーを登録
         */
        on(event, callback) {
            if (this.listeners[event]) {
                this.listeners[event].push(callback);
            }
        }

        /**
         * イベントを発火
         */
        emit(event, data) {
            if (this.listeners[event]) {
                this.listeners[event].forEach(callback => callback(data));
            }
        }

        /**
         * タイマー開始
         */
        start() {
            if (this.state === TimerState.RUNNING) {
                return;
            }

            this.state = TimerState.RUNNING;
            this.emit('stateChange', { state: this.state, mode: this.mode });

            this.intervalId = setInterval(() => {
                this.tick();
            }, 1000);
        }

        /**
         * タイマー一時停止
         */
        pause() {
            if (this.state !== TimerState.RUNNING) {
                return;
            }

            this.state = TimerState.PAUSED;
            this.emit('stateChange', { state: this.state, mode: this.mode });

            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
            }
        }

        /**
         * タイマーリセット
         */
        reset() {
            this.pause();
            this.state = TimerState.IDLE;
            this.mode = TimerMode.WORK;
            this.remainingTime = WORK_DURATION;
            this.totalTime = WORK_DURATION;

            this.emit('stateChange', { state: this.state, mode: this.mode });
            this.emit('tick', {
                remainingTime: this.remainingTime,
                totalTime: this.totalTime,
                progress: 0
            });
        }

        /**
         * 1秒ごとの更新処理
         */
        tick() {
            if (this.state !== TimerState.RUNNING) {
                return;
            }

            this.remainingTime--;

            const progress = 1 - (this.remainingTime / this.totalTime);
            this.emit('tick', {
                remainingTime: this.remainingTime,
                totalTime: this.totalTime,
                progress: progress
            });

            // タイマー完了
            if (this.remainingTime <= 0) {
                this.complete();
            }
        }

        /**
         * タイマー完了処理
         */
        complete() {
            this.pause();
            this.state = TimerState.COMPLETED;

            // 作業モード完了時は進捗を更新
            if (this.mode === TimerMode.WORK) {
                this.todayStats.completed++;
                this.todayStats.focusTimeMinutes += Math.floor(WORK_DURATION / 60);
                this.saveTodayStats();
            }

            this.emit('complete', {
                mode: this.mode,
                stats: this.todayStats
            });

            // 次のモードに自動切替（3秒後）
            setTimeout(() => {
                this.switchMode();
            }, 3000);
        }

        /**
         * モード切替（作業 ⇔ 休憩）
         */
        switchMode() {
            if (this.mode === TimerMode.WORK) {
                this.mode = TimerMode.BREAK;
                this.totalTime = BREAK_DURATION;
                this.remainingTime = BREAK_DURATION;
            } else {
                this.mode = TimerMode.WORK;
                this.totalTime = WORK_DURATION;
                this.remainingTime = WORK_DURATION;
            }

            this.state = TimerState.IDLE;
            this.emit('modeChange', { mode: this.mode });
            this.emit('stateChange', { state: this.state, mode: this.mode });
            this.emit('tick', {
                remainingTime: this.remainingTime,
                totalTime: this.totalTime,
                progress: 0
            });
        }

        /**
         * 現在の状態を取得
         */
        getState() {
            return {
                state: this.state,
                mode: this.mode,
                remainingTime: this.remainingTime,
                totalTime: this.totalTime,
                progress: 1 - (this.remainingTime / this.totalTime),
                stats: this.todayStats
            };
        }

        /**
         * 今日の進捗をlocalStorageに保存
         */
        saveTodayStats() {
            const today = new Date().toDateString();
            const data = {
                date: today,
                stats: this.todayStats
            };
            localStorage.setItem('pomodoroStats', JSON.stringify(data));
        }

        /**
         * 今日の進捗をlocalStorageから読み込み
         */
        loadTodayStats() {
            const today = new Date().toDateString();
            const stored = localStorage.getItem('pomodoroStats');
            
            if (stored) {
                try {
                    const data = JSON.parse(stored);
                    // 同じ日付であれば復元
                    if (data.date === today) {
                        this.todayStats = data.stats;
                    }
                } catch (error) {
                    // 破損したデータの場合は無視してデフォルト値を使用
                    console.warn('Failed to parse stored stats:', error);
                }
            }
        }
    }

    // グローバルに公開
    window.TimerEngine = TimerEngine;
    window.TimerState = TimerState;
    window.TimerMode = TimerMode;

})(window);
