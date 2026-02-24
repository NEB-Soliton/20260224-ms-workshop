/**
 * UI モジュール - DOM 更新処理
 * IIFE パターンで実装し、window オブジェクトにエクスポート
 */
(function(window) {
    'use strict';

    /**
     * UI クラス
     */
    class UI {
        constructor() {
            // DOM 要素の取得
            this.elements = {
                modeDisplay: document.getElementById('modeDisplay'),
                modeText: document.getElementById('modeText'),
                timeText: document.getElementById('timeText'),
                progressFill: document.getElementById('progressFill'),
                completionMessage: document.getElementById('completionMessage'),
                startBtn: document.getElementById('startBtn'),
                pauseBtn: document.getElementById('pauseBtn'),
                resetBtn: document.getElementById('resetBtn')
            };
        }

        /**
         * 時間表示を更新
         */
        updateTime(seconds, formatTime) {
            const formattedTime = formatTime(seconds);
            this.elements.timeText.textContent = formattedTime;
        }

        /**
         * モード表示を更新
         */
        updateMode(mode) {
            // モードテキストを更新
            if (mode === 'work') {
                this.elements.modeText.textContent = '作業モード';
            } else if (mode === 'break') {
                this.elements.modeText.textContent = '休憩モード';
            }

            // モード別のスタイルを適用
            this.elements.modeDisplay.classList.remove('mode-work', 'mode-break', 'mode-completed');
            this.elements.modeDisplay.classList.add(`mode-${mode}`);
        }

        /**
         * プログレスバーを更新
         */
        updateProgress(progress) {
            this.elements.progressFill.style.width = `${progress}%`;
        }

        /**
         * 完了メッセージを表示
         */
        showCompletion(mode) {
            const message = mode === 'work' 
                ? '✓ 作業セッション完了！休憩を取りましょう。' 
                : '✓ 休憩完了！次の作業を始めましょう。';
            
            this.elements.completionMessage.querySelector('p').textContent = message;
            this.elements.completionMessage.style.display = 'block';
            
            // 5秒後に自動的に非表示
            setTimeout(() => {
                this.hideCompletion();
            }, 5000);
        }

        /**
         * 完了メッセージを非表示
         */
        hideCompletion() {
            this.elements.completionMessage.style.display = 'none';
        }

        /**
         * ボタンの状態を更新
         */
        updateButtons(state) {
            switch (state) {
                case 'idle':
                    this.elements.startBtn.disabled = false;
                    this.elements.pauseBtn.disabled = true;
                    this.elements.resetBtn.disabled = false;
                    this.elements.startBtn.textContent = '開始';
                    break;
                
                case 'running':
                    this.elements.startBtn.disabled = true;
                    this.elements.pauseBtn.disabled = false;
                    this.elements.resetBtn.disabled = false;
                    break;
                
                case 'paused':
                    this.elements.startBtn.disabled = false;
                    this.elements.pauseBtn.disabled = true;
                    this.elements.resetBtn.disabled = false;
                    this.elements.startBtn.textContent = '再開';
                    break;
                
                case 'completed':
                    this.elements.startBtn.disabled = false;
                    this.elements.pauseBtn.disabled = true;
                    this.elements.resetBtn.disabled = false;
                    this.elements.startBtn.textContent = '次のセッション';
                    this.elements.modeDisplay.classList.add('mode-completed');
                    break;
            }
        }

        /**
         * 初期状態を表示
         */
        init(engine) {
            const state = engine.getState();
            this.updateTime(state.remainingSeconds, engine.formatTime.bind(engine));
            this.updateMode(state.mode);
            this.updateProgress(state.progress);
            this.updateButtons(state.state);
        }
    }

    // window オブジェクトにエクスポート
    window.UI = UI;

})(window);
