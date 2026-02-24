/**
 * アプリケーションメインファイル - イベント配線
 */
(function() {
    'use strict';

    // グローバル変数
    let timerEngine;
    let uiController;
    let audioContext; // AudioContext を再利用

    /**
     * DOMContentLoaded時の初期化
     */
    document.addEventListener('DOMContentLoaded', function() {
        // インスタンス作成
        timerEngine = new window.TimerEngine();
        uiController = new window.UIController();

        // UI初期化
        uiController.initialize(timerEngine.getState());

        // イベントリスナー設定
        setupTimerListeners();
        setupButtonListeners();
    });

    /**
     * タイマーエンジンのイベントリスナー設定
     */
    function setupTimerListeners() {
        // タイマーティック（1秒ごと）
        timerEngine.on('tick', function(data) {
            uiController.updateTime(data.remainingTime);
            uiController.updateProgress(data.progress);
        });

        // 状態変更
        timerEngine.on('stateChange', function(data) {
            uiController.updateMode(data.mode, data.state);
            uiController.updateButtons(data.state);
        });

        // モード変更
        timerEngine.on('modeChange', function(data) {
            uiController.updateMode(data.mode, timerEngine.getState().state);
        });

        // 完了
        timerEngine.on('complete', function(data) {
            uiController.updateStats(data.stats);
            uiController.updateMode(data.mode, window.TimerState.COMPLETED);
            uiController.updateButtons(window.TimerState.COMPLETED);
            
            // 完了音を再生（オプション）
            playCompletionSound();
        });
    }

    /**
     * ボタンのイベントリスナー設定
     */
    function setupButtonListeners() {
        const startBtn = document.getElementById('startBtn');
        const resetBtn = document.getElementById('resetBtn');

        // 開始/一時停止ボタン
        startBtn.addEventListener('click', function() {
            const state = timerEngine.getState().state;
            
            if (state === window.TimerState.RUNNING) {
                timerEngine.pause();
            } else {
                timerEngine.start();
            }
        });

        // リセットボタン
        resetBtn.addEventListener('click', function() {
            timerEngine.reset();
        });

        // ウィンドウコントロールボタン（装飾用、機能なし）
        const controlBtns = document.querySelectorAll('.control-btn');
        controlBtns.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                // モックなので何もしない
            });
        });
    }

    /**
     * 完了音を再生
     */
    function playCompletionSound() {
        // Web Audio APIを使用してシンプルなビープ音を生成
        try {
            // AudioContext を初回のみ作成（リソースリーク防止）
            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 800; // 周波数: 800Hz
            oscillator.type = 'sine'; // 波形: サイン波

            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.log('Audio playback not supported:', error);
        }
    }

})();
