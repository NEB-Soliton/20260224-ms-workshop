/**
 * UI更新モジュール - DOM操作
 */
(function(window) {
    'use strict';

    /**
     * UIコントローラークラス
     */
    class UIController {
        constructor() {
            // DOM要素の参照
            this.elements = {
                timeDisplay: document.getElementById('timeDisplay'),
                modeDisplay: document.getElementById('modeDisplay'),
                progressCircle: document.getElementById('progressCircle'),
                completedCount: document.getElementById('completedCount'),
                focusTime: document.getElementById('focusTime'),
                startBtn: document.getElementById('startBtn'),
                resetBtn: document.getElementById('resetBtn'),
                timerCard: document.querySelector('.timer-card')
            };

            // プログレスリングの設定
            this.progressCircleRadius = 120;
            this.progressCircleCircumference = 2 * Math.PI * this.progressCircleRadius;
        }

        /**
         * 時間表示を更新
         * @param {number} seconds - 残り秒数
         */
        updateTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const secs = seconds % 60;
            const timeString = `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            this.elements.timeDisplay.textContent = timeString;
        }

        /**
         * モード表示を更新
         * @param {string} mode - 'work' または 'break'
         * @param {string} state - タイマーの状態
         */
        updateMode(mode, state) {
            // モード切替時のクラス更新
            this.elements.timerCard.classList.remove('break-mode', 'completed');
            
            if (mode === window.TimerMode.BREAK) {
                this.elements.modeDisplay.textContent = '休憩中';
                this.elements.timerCard.classList.add('break-mode');
            } else {
                this.elements.modeDisplay.textContent = '作業中';
            }

            // 完了状態の表示
            if (state === window.TimerState.COMPLETED) {
                this.elements.timerCard.classList.add('completed');
                if (mode === window.TimerMode.WORK) {
                    this.elements.modeDisplay.textContent = '完了！';
                } else {
                    this.elements.modeDisplay.textContent = '休憩終了';
                }
            }
        }

        /**
         * プログレスリングを更新
         * @param {number} progress - 進捗率 (0.0 ~ 1.0)
         */
        updateProgress(progress) {
            const offset = this.progressCircleCircumference * (1 - progress);
            this.elements.progressCircle.style.strokeDashoffset = offset;
        }

        /**
         * 今日の進捗を更新
         * @param {object} stats - {completed: number, focusTimeMinutes: number}
         */
        updateStats(stats) {
            this.elements.completedCount.textContent = stats.completed.toString();
            
            // 集中時間を「X時間Y分」形式で表示
            const hours = Math.floor(stats.focusTimeMinutes / 60);
            const minutes = stats.focusTimeMinutes % 60;
            
            if (hours > 0) {
                this.elements.focusTime.textContent = `${hours}時間${minutes}分`;
            } else {
                this.elements.focusTime.textContent = `${minutes}分`;
            }
        }

        /**
         * ボタンの状態を更新
         * @param {string} state - タイマーの状態
         */
        updateButtons(state) {
            if (state === window.TimerState.RUNNING) {
                this.elements.startBtn.textContent = '一時停止';
                this.elements.startBtn.disabled = false;
                this.elements.resetBtn.disabled = false;
            } else if (state === window.TimerState.PAUSED) {
                this.elements.startBtn.textContent = '再開';
                this.elements.startBtn.disabled = false;
                this.elements.resetBtn.disabled = false;
            } else if (state === window.TimerState.COMPLETED) {
                this.elements.startBtn.textContent = '開始';
                this.elements.startBtn.disabled = true;
                this.elements.resetBtn.disabled = false;
            } else {
                // IDLE
                this.elements.startBtn.textContent = '開始';
                this.elements.startBtn.disabled = false;
                this.elements.resetBtn.disabled = false;
            }
        }

        /**
         * すべての表示を初期化
         * @param {object} state - タイマーの状態オブジェクト
         */
        initialize(state) {
            this.updateTime(state.remainingTime);
            this.updateMode(state.mode, state.state);
            this.updateProgress(state.progress);
            this.updateStats(state.stats);
            this.updateButtons(state.state);

            // プログレスリングの初期設定
            this.elements.progressCircle.style.strokeDasharray = this.progressCircleCircumference;
            this.elements.progressCircle.style.strokeDashoffset = this.progressCircleCircumference;
        }
    }

    // グローバルに公開
    window.UIController = UIController;

})(window);
