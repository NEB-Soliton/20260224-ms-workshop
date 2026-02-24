/**
 * UI Module
 * 
 * タイマーエンジンとDOM要素を連携し、画面表示を更新する
 */

(function(window) {
    'use strict';

    /**
     * UI クラス
     * DOM操作とタイマー表示の更新を担当
     */
    class UI {
        constructor() {
            // DOM要素を取得
            this.timeDisplay = document.getElementById('time-display');
            this.modeDisplay = document.getElementById('mode-display');
            this.timerCard = document.querySelector('.timer-card');
            this.progressRing = document.querySelector('.progress-ring-progress');
            this.todayCount = document.getElementById('today-count');
            this.weekCount = document.getElementById('week-count');
            
            // プログレスリングの円周を計算（2πr, r=110）
            this.circumference = 2 * Math.PI * 110;
            
            // 初期状態を設定
            this.progressRing.style.strokeDasharray = this.circumference;
            this.progressRing.style.strokeDashoffset = 0;
        }

        /**
         * 時間表示を更新
         * @param {number} milliseconds - ミリ秒単位の時間
         */
        updateTime(milliseconds) {
            const totalSeconds = Math.ceil(milliseconds / 1000);
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = totalSeconds % 60;
            
            // MM:SS 形式でフォーマット
            const timeString = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            this.timeDisplay.textContent = timeString;
        }

        /**
         * モード表示を更新
         * @param {string} mode - タイマーモード ('work' or 'break')
         */
        updateMode(mode) {
            if (mode === 'work') {
                this.modeDisplay.textContent = '作業時間';
            } else if (mode === 'break') {
                this.modeDisplay.textContent = '休憩時間';
            }
        }

        /**
         * プログレスリングを更新
         * @param {number} progress - 進捗率 (0.0 ~ 1.0, 経過時間/総時間)
         */
        updateProgress(progress) {
            // 進捗率に応じてstroke-dashoffsetを計算
            // progress 0 (開始) → offset 0 (満タン、リングが見える)
            // progress 1 (終了) → offset circumference (空、リングが消える)
            const offset = this.circumference * progress;
            this.progressRing.style.strokeDashoffset = offset;
        }

        /**
         * タイマーカードの状態クラスを更新
         * @param {string} state - タイマーの状態
         */
        updateState(state) {
            // 既存の状態クラスを削除
            this.timerCard.classList.remove('running', 'paused', 'completed');
            
            // 新しい状態クラスを追加
            if (state === 'running') {
                this.timerCard.classList.add('running');
            } else if (state === 'paused') {
                this.timerCard.classList.add('paused');
            } else if (state === 'completed') {
                this.timerCard.classList.add('completed');
            }
        }

        /**
         * ボタンの有効/無効状態を更新
         * @param {string} state - タイマーの状態
         */
        updateButtons(state) {
            const startBtn = document.getElementById('start-btn');
            const pauseBtn = document.getElementById('pause-btn');
            const resetBtn = document.getElementById('reset-btn');

            if (state === 'idle') {
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                resetBtn.disabled = false;
                startBtn.textContent = 'スタート';
            } else if (state === 'running') {
                startBtn.disabled = true;
                pauseBtn.disabled = false;
                resetBtn.disabled = false;
                pauseBtn.textContent = '一時停止';
            } else if (state === 'paused') {
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                resetBtn.disabled = false;
                startBtn.textContent = '再開';
            } else if (state === 'completed') {
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                resetBtn.disabled = false;
                startBtn.textContent = '次へ';
            }
        }

        /**
         * 統計情報を更新
         * @param {number} today - 今日の完了数
         * @param {number} week - 今週の完了数
         */
        updateStats(today, week) {
            this.todayCount.textContent = today;
            this.weekCount.textContent = week;
        }

        /**
         * タイマー情報を全て更新
         * @param {Object} timerData - タイマーの状態データ
         */
        updateAll(timerData) {
            this.updateTime(timerData.remainingTime);
            this.updateMode(timerData.mode);
            this.updateProgress(timerData.progress || 0);
            this.updateState(timerData.state);
            this.updateButtons(timerData.state);
        }

        /**
         * 完了通知を表示
         */
        showCompletionNotification(mode) {
            // ブラウザ通知APIが利用可能な場合
            if ('Notification' in window && Notification.permission === 'granted') {
                const title = mode === 'work' ? '作業完了！' : '休憩完了！';
                const body = mode === 'work' 
                    ? '素晴らしい集中力でした！休憩しましょう。' 
                    : '休憩が終わりました。次の作業を始めましょう！';
                
                new Notification(title, {
                    body: body
                });
            }
        }

        /**
         * 通知権限をリクエスト
         */
        requestNotificationPermission() {
            if ('Notification' in window && Notification.permission === 'default') {
                Notification.requestPermission();
            }
        }
    }

    // グローバルに公開
    window.UI = UI;

})(window);
