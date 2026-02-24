/**
 * アプリケーション - イベント配線とエンジン・UI の連携
 */
(function() {
    'use strict';

    // DOM 読み込み完了後に初期化
    document.addEventListener('DOMContentLoaded', function() {
        
        // エンジンと UI のインスタンス化
        const engine = new TimerEngine();
        const ui = new UI();
        
        // 初期状態を表示
        ui.init(engine);
        
        // === エンジンのイベントを UI に接続 ===
        
        // tick イベント: 時間とプログレスバーを更新
        engine.on('tick', function(data) {
            ui.updateTime(data.remainingSeconds, engine.formatTime.bind(engine));
            ui.updateProgress(data.progress);
        });
        
        // stateChange イベント: ボタンの状態を更新
        engine.on('stateChange', function(data) {
            ui.updateButtons(data.state);
        });
        
        // modeChange イベント: モード表示を更新
        engine.on('modeChange', function(data) {
            ui.updateMode(data.mode);
        });
        
        // complete イベント: 完了メッセージを表示
        engine.on('complete', function(data) {
            ui.showCompletion(data.mode);
        });
        
        // === ボタンのイベントリスナーを設定 ===
        
        // 開始/再開ボタン
        ui.elements.startBtn.addEventListener('click', function() {
            engine.start();
        });
        
        // 一時停止ボタン
        ui.elements.pauseBtn.addEventListener('click', function() {
            engine.pause();
        });
        
        // リセットボタン
        ui.elements.resetBtn.addEventListener('click', function() {
            engine.reset();
            ui.hideCompletion();
        });

    });

})();
