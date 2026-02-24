/**
 * App Module
 * 
 * タイマーエンジンとUIを連携し、イベントを配線する
 */

(function() {
    'use strict';

    // アプリケーション初期化
    document.addEventListener('DOMContentLoaded', function() {
        // タイマーエンジンとUIを初期化
        const timerEngine = new TimerEngine();
        const ui = new UI();

        // 統計情報（localStorageから読み込み）
        let stats = loadStats();
        ui.updateStats(stats.today, stats.week);

        // 通知権限をリクエスト
        ui.requestNotificationPermission();

        // ボタン要素を取得
        const startBtn = document.getElementById('start-btn');
        const pauseBtn = document.getElementById('pause-btn');
        const resetBtn = document.getElementById('reset-btn');

        // タイマーエンジンのイベントリスナーを登録
        
        // tick イベント - 毎回の時間更新
        timerEngine.on('tick', function(data) {
            ui.updateAll(data);
        });

        // stateChange イベント - 状態変更時
        timerEngine.on('stateChange', function(data) {
            ui.updateState(data.newState);
            ui.updateButtons(data.newState);
        });

        // complete イベント - タイマー完了時
        timerEngine.on('complete', function(data) {
            // 統計を更新
            if (data.mode === 'work') {
                stats.today++;
                stats.week++;
                saveStats(stats);
                ui.updateStats(stats.today, stats.week);
            }
            
            // 完了通知を表示
            ui.showCompletionNotification(data.mode);
        });

        // ボタンのイベントリスナーを登録
        
        // スタート/再開ボタン
        startBtn.addEventListener('click', function() {
            const state = timerEngine.getState();
            
            if (state.state === 'idle') {
                timerEngine.start();
            } else if (state.state === 'paused') {
                timerEngine.resume();
            } else if (state.state === 'completed') {
                // 完了後は次のモードに切り替え
                timerEngine.switchMode();
                timerEngine.start();
            }
        });

        // 一時停止ボタン
        pauseBtn.addEventListener('click', function() {
            timerEngine.pause();
        });

        // リセットボタン
        resetBtn.addEventListener('click', function() {
            timerEngine.reset();
        });

        // 初期表示を更新
        const initialState = timerEngine.getState();
        ui.updateAll({
            remainingTime: initialState.remainingTime,
            elapsedTime: initialState.elapsedTime,
            progress: 0,
            state: initialState.state,
            mode: initialState.mode
        });
    });

    /**
     * 統計情報をlocalStorageから読み込み
     */
    function loadStats() {
        const savedStats = localStorage.getItem('pomodoroStats');
        
        if (savedStats) {
            try {
                const stats = JSON.parse(savedStats);
                const today = new Date().toDateString();
                
                // 日付が変わっていたら今日のカウントをリセット
                if (stats.lastDate !== today) {
                    stats.today = 0;
                    stats.lastDate = today;
                }
                
                return stats;
            } catch (e) {
                console.error('Failed to load stats:', e);
            }
        }
        
        // デフォルト値
        return {
            today: 0,
            week: 0,
            lastDate: new Date().toDateString()
        };
    }

    /**
     * 統計情報をlocalStorageに保存
     */
    function saveStats(stats) {
        try {
            localStorage.setItem('pomodoroStats', JSON.stringify(stats));
        } catch (e) {
            console.error('Failed to save stats:', e);
        }
    }

})();
