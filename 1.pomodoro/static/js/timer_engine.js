/**
 * Pomodoro Timer Engine
 * 
 * 状態遷移と時間計算を管理するコアエンジン
 * 
 * 状態:
 * - idle: 初期状態（タイマー未開始）
 * - running: タイマー動作中
 * - paused: 一時停止中
 * - completed: タイマー完了
 */

(function(window) {
    'use strict';

    /**
     * タイマーの状態定数
     */
    const TimerState = {
        IDLE: 'idle',
        RUNNING: 'running',
        PAUSED: 'paused',
        COMPLETED: 'completed'
    };

    /**
     * タイマーモード
     */
    const TimerMode = {
        WORK: 'work',
        BREAK: 'break'
    };

    /**
     * TimerEngine クラス
     * ポモドーロタイマーのコアロジックを実装
     */
    class TimerEngine {
        constructor() {
            // 状態管理
            this.state = TimerState.IDLE;
            this.mode = TimerMode.WORK;
            
            // 時間設定（ミリ秒）
            this.workDuration = 25 * 60 * 1000; // 25分
            this.breakDuration = 5 * 60 * 1000; // 5分
            
            // タイマー管理
            this.targetTimestamp = null;  // 目標終了時刻
            this.remainingTime = this.workDuration; // 残り時間
            this.elapsedTime = 0; // 経過時間
            
            // 一時停止時の残り時間保存
            this.pausedRemainingTime = null;
            
            // ティック間隔（ミリ秒）
            this.tickInterval = 100;
            this.tickTimer = null;
            
            // イベントリスナー
            this.listeners = {
                tick: [],
                stateChange: [],
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
            if (this.state === TimerState.RUNNING) {
                return; // 既に実行中の場合は何もしない
            }

            // 目標時刻を設定（現在時刻 + 残り時間）
            const now = Date.now();
            this.targetTimestamp = now + this.remainingTime;
            
            // 状態を変更
            this.setState(TimerState.RUNNING);
            
            // ティック処理を開始
            this.startTicking();
        }

        /**
         * タイマーを一時停止
         */
        pause() {
            if (this.state !== TimerState.RUNNING) {
                return; // 実行中でない場合は何もしない
            }

            // ティック処理を停止
            this.stopTicking();
            
            // 現在の残り時間を保存
            this.pausedRemainingTime = this.remainingTime;
            
            // 状態を変更
            this.setState(TimerState.PAUSED);
        }

        /**
         * タイマーを再開
         */
        resume() {
            if (this.state !== TimerState.PAUSED) {
                return; // 一時停止中でない場合は何もしない
            }

            // 新しい目標時刻を設定
            const now = Date.now();
            this.targetTimestamp = now + this.pausedRemainingTime;
            this.remainingTime = this.pausedRemainingTime;
            
            // 状態を変更
            this.setState(TimerState.RUNNING);
            
            // ティック処理を開始
            this.startTicking();
        }

        /**
         * タイマーをリセット
         */
        reset() {
            // ティック処理を停止
            this.stopTicking();
            
            // 状態をリセット
            this.targetTimestamp = null;
            this.pausedRemainingTime = null;
            this.elapsedTime = 0;
            
            // 現在のモードに応じた初期時間を設定
            if (this.mode === TimerMode.WORK) {
                this.remainingTime = this.workDuration;
            } else {
                this.remainingTime = this.breakDuration;
            }
            
            // 状態を変更
            this.setState(TimerState.IDLE);
            
            // UI更新のためにtickイベントを発火
            this.emitTick();
        }

        /**
         * 状態を変更
         */
        setState(newState) {
            const oldState = this.state;
            this.state = newState;
            this.emit('stateChange', { oldState, newState, mode: this.mode });
        }

        /**
         * モードを切り替え（作業 ⇔ 休憩）
         */
        switchMode() {
            if (this.mode === TimerMode.WORK) {
                this.mode = TimerMode.BREAK;
                this.remainingTime = this.breakDuration;
            } else {
                this.mode = TimerMode.WORK;
                this.remainingTime = this.workDuration;
            }
            this.reset();
        }

        /**
         * ティック処理を開始
         */
        startTicking() {
            this.tickTimer = setInterval(() => {
                this.tick();
            }, this.tickInterval);
        }

        /**
         * ティック処理を停止
         */
        stopTicking() {
            if (this.tickTimer) {
                clearInterval(this.tickTimer);
                this.tickTimer = null;
            }
        }

        /**
         * ティック処理（毎回実行される）
         */
        tick() {
            if (this.state !== TimerState.RUNNING) {
                return;
            }

            const now = Date.now();
            
            // 残り時間を計算（targetTimestamp - now）
            this.remainingTime = Math.max(0, this.targetTimestamp - now);
            
            // 経過時間を計算
            const totalDuration = this.mode === TimerMode.WORK 
                ? this.workDuration 
                : this.breakDuration;
            this.elapsedTime = totalDuration - this.remainingTime;

            // タイマー完了判定
            if (this.remainingTime <= 0) {
                this.complete();
                return;
            }

            // tick イベントを発火
            this.emitTick();
        }

        /**
         * tick イベントを発火
         */
        emitTick() {
            const totalDuration = this.mode === TimerMode.WORK 
                ? this.workDuration 
                : this.breakDuration;
            
            const progress = this.elapsedTime / totalDuration;
            
            this.emit('tick', {
                remainingTime: this.remainingTime,
                elapsedTime: this.elapsedTime,
                totalDuration: totalDuration,
                progress: progress,
                state: this.state,
                mode: this.mode
            });
        }

        /**
         * タイマー完了処理
         */
        complete() {
            // ティック処理を停止
            this.stopTicking();
            
            // 残り時間を0に設定
            this.remainingTime = 0;
            
            // 状態を変更
            this.setState(TimerState.COMPLETED);
            
            // complete イベントを発火
            this.emit('complete', { mode: this.mode });
            
            // 最終のtickイベントを発火
            this.emitTick();
        }

        /**
         * 現在の状態を取得
         */
        getState() {
            return {
                state: this.state,
                mode: this.mode,
                remainingTime: this.remainingTime,
                elapsedTime: this.elapsedTime,
                totalDuration: this.mode === TimerMode.WORK 
                    ? this.workDuration 
                    : this.breakDuration
            };
        }

        /**
         * 作業時間を設定（分単位）
         */
        setWorkDuration(minutes) {
            this.workDuration = minutes * 60 * 1000;
            if (this.mode === TimerMode.WORK && this.state === TimerState.IDLE) {
                this.remainingTime = this.workDuration;
                this.emitTick();
            }
        }

        /**
         * 休憩時間を設定（分単位）
         */
        setBreakDuration(minutes) {
            this.breakDuration = minutes * 60 * 1000;
            if (this.mode === TimerMode.BREAK && this.state === TimerState.IDLE) {
                this.remainingTime = this.breakDuration;
                this.emitTick();
            }
        }
    }

    // グローバルに公開
    window.TimerEngine = TimerEngine;
    window.TimerState = TimerState;
    window.TimerMode = TimerMode;

})(window);
