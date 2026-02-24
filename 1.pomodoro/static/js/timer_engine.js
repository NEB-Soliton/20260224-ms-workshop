/**
 * タイマーエンジン - ポモドーロタイマーのコア機能
 * IIFE パターンで実装し、window オブジェクトにエクスポート
 */
(function(window) {
    'use strict';

    /**
     * タイマーエンジンクラス
     */
    class TimerEngine {
        constructor() {
            // タイマー設定（分単位）
            this.WORK_DURATION = 25;
            this.BREAK_DURATION = 5;
            
            // 状態管理
            this.state = 'idle'; // idle, running, paused, completed
            this.mode = 'work'; // work, break
            this.remainingSeconds = this.WORK_DURATION * 60;
            this.totalSeconds = this.WORK_DURATION * 60;
            this.intervalId = null;
            
            // イベントリスナー
            this.listeners = {
                tick: [],
                stateChange: [],
                modeChange: [],
                complete: []
            };
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
         * タイマーを開始
         */
        start() {
            if (this.state === 'running') return;
            
            this.state = 'running';
            this.emit('stateChange', { state: this.state, mode: this.mode });
            
            this.intervalId = setInterval(() => {
                this.tick();
            }, 1000);
        }

        /**
         * タイマーを一時停止
         */
        pause() {
            if (this.state !== 'running') return;
            
            this.state = 'paused';
            this.emit('stateChange', { state: this.state, mode: this.mode });
            
            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
            }
        }

        /**
         * タイマーをリセット
         */
        reset() {
            this.pause();
            
            this.state = 'idle';
            this.mode = 'work';
            this.remainingSeconds = this.WORK_DURATION * 60;
            this.totalSeconds = this.WORK_DURATION * 60;
            
            this.emit('stateChange', { state: this.state, mode: this.mode });
            this.emit('modeChange', { mode: this.mode });
            this.emit('tick', {
                remainingSeconds: this.remainingSeconds,
                totalSeconds: this.totalSeconds,
                progress: 0
            });
        }

        /**
         * 1秒ごとの処理
         */
        tick() {
            // タイマー終了チェック
            if (this.remainingSeconds <= 0) {
                this.onTimerComplete();
                return;
            }
            
            this.remainingSeconds--;
            
            const progress = ((this.totalSeconds - this.remainingSeconds) / this.totalSeconds) * 100;
            
            this.emit('tick', {
                remainingSeconds: this.remainingSeconds,
                totalSeconds: this.totalSeconds,
                progress: progress
            });
        }

        /**
         * タイマー完了時の処理
         */
        onTimerComplete() {
            this.pause();
            
            this.state = 'completed';
            this.emit('complete', { mode: this.mode });
            this.emit('stateChange', { state: this.state, mode: this.mode });
            
            // 次のモードに切り替え
            if (this.mode === 'work') {
                this.mode = 'break';
                this.remainingSeconds = this.BREAK_DURATION * 60;
                this.totalSeconds = this.BREAK_DURATION * 60;
            } else {
                this.mode = 'work';
                this.remainingSeconds = this.WORK_DURATION * 60;
                this.totalSeconds = this.WORK_DURATION * 60;
            }
            
            this.emit('modeChange', { mode: this.mode });
            this.emit('tick', {
                remainingSeconds: this.remainingSeconds,
                totalSeconds: this.totalSeconds,
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
                remainingSeconds: this.remainingSeconds,
                totalSeconds: this.totalSeconds,
                progress: ((this.totalSeconds - this.remainingSeconds) / this.totalSeconds) * 100
            };
        }

        /**
         * 時間を分:秒形式にフォーマット
         */
        formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
    }

    // window オブジェクトにエクスポート
    window.TimerEngine = TimerEngine;

})(window);
