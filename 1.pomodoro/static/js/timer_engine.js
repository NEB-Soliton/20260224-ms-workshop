/**
 * Timer Engine - State management and time calculation
 * タイマーエンジン - 状態管理と時間計算
 */

(function(window) {
    'use strict';

    const TimerState = {
        IDLE: 'idle',
        RUNNING: 'running',
        PAUSED: 'paused',
        COMPLETED: 'completed'
    };

    const TimerMode = {
        WORK: 'work',
        BREAK: 'break'
    };

    class TimerEngine {
        constructor(workDuration = 25, breakDuration = 5) {
            this.workDuration = workDuration * 60; // Convert to seconds
            this.breakDuration = breakDuration * 60; // Convert to seconds
            this.state = TimerState.IDLE;
            this.mode = TimerMode.WORK;
            this.targetTimestamp = null;
            this.remainingTime = this.workDuration;
            this.intervalId = null;
            this.onTick = null;
            this.onComplete = null;
            this.onStateChange = null;
        }

        start() {
            if (this.state === TimerState.RUNNING) {
                return false;
            }

            if (this.state === TimerState.IDLE) {
                // First start - set initial duration
                this.remainingTime = this.mode === TimerMode.WORK ? this.workDuration : this.breakDuration;
            }

            // Calculate target timestamp
            this.targetTimestamp = Date.now() + (this.remainingTime * 1000);
            this.state = TimerState.RUNNING;
            this._notifyStateChange();
            
            // Start interval
            this.intervalId = setInterval(() => this._tick(), 100);
            
            return true;
        }

        pause() {
            if (this.state !== TimerState.RUNNING) {
                return false;
            }

            // Update remaining time before pausing
            this.remainingTime = this.getRemainingTime();
            
            // Clear interval
            clearInterval(this.intervalId);
            this.intervalId = null;
            
            this.state = TimerState.PAUSED;
            this._notifyStateChange();
            
            return true;
        }

        resume() {
            if (this.state !== TimerState.PAUSED) {
                return false;
            }

            return this.start();
        }

        reset() {
            // Clear interval
            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
            }

            // Reset state
            this.state = TimerState.IDLE;
            this.targetTimestamp = null;
            this.remainingTime = this.mode === TimerMode.WORK ? this.workDuration : this.breakDuration;
            
            this._notifyStateChange();
            this._notifyTick();
            
            return true;
        }

        switchMode() {
            this.reset();
            this.mode = this.mode === TimerMode.WORK ? TimerMode.BREAK : TimerMode.WORK;
            this.remainingTime = this.mode === TimerMode.WORK ? this.workDuration : this.breakDuration;
            this._notifyStateChange();
            this._notifyTick();
        }

        getRemainingTime() {
            if (this.state !== TimerState.RUNNING) {
                return Math.max(0, this.remainingTime);
            }

            const remaining = Math.max(0, (this.targetTimestamp - Date.now()) / 1000);
            return remaining;
        }

        getProgress() {
            const duration = this.mode === TimerMode.WORK ? this.workDuration : this.breakDuration;
            const remaining = this.getRemainingTime();
            return 1 - (remaining / duration);
        }

        getState() {
            return {
                state: this.state,
                mode: this.mode,
                remainingTime: this.getRemainingTime(),
                progress: this.getProgress(),
                isRunning: this.state === TimerState.RUNNING,
                isPaused: this.state === TimerState.PAUSED,
                isIdle: this.state === TimerState.IDLE,
                isCompleted: this.state === TimerState.COMPLETED
            };
        }

        setWorkDuration(minutes) {
            this.workDuration = minutes * 60;
            if (this.mode === TimerMode.WORK && this.state === TimerState.IDLE) {
                this.remainingTime = this.workDuration;
            }
        }

        setBreakDuration(minutes) {
            this.breakDuration = minutes * 60;
            if (this.mode === TimerMode.BREAK && this.state === TimerState.IDLE) {
                this.remainingTime = this.breakDuration;
            }
        }

        _tick() {
            const remaining = this.getRemainingTime();
            
            if (remaining <= 0) {
                // Timer completed
                clearInterval(this.intervalId);
                this.intervalId = null;
                this.state = TimerState.COMPLETED;
                this.remainingTime = 0;
                
                this._notifyStateChange();
                this._notifyComplete();
            } else {
                this._notifyTick();
            }
        }

        _notifyTick() {
            if (this.onTick) {
                this.onTick(this.getState());
            }
        }

        _notifyComplete() {
            if (this.onComplete) {
                this.onComplete(this.getState());
            }
        }

        _notifyStateChange() {
            if (this.onStateChange) {
                this.onStateChange(this.getState());
            }
        }
    }

    // Export to window
    window.TimerEngine = TimerEngine;
    window.TimerState = TimerState;
    window.TimerMode = TimerMode;

})(window);
