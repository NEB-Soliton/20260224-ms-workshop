// グローバル変数
let timer;
let timeLeft;
let totalTime;
let isRunning = false;
let isWorkSession = true;
let sessionCount = 0;

// AudioContextを一度だけ作成
let audioContext = null;

// 設定
let settings = {
    workTime: 25,
    breakTime: 5,
    theme: 'light',
    sounds: {
        start: true,
        end: true,
        tick: false
    }
};

// ローカルストレージから設定を読み込み
function loadSettings() {
    const saved = localStorage.getItem('pomodoroSettings');
    if (saved) {
        settings = JSON.parse(saved);
        applySettings();
    }
}

// 設定を保存
function saveSettings() {
    localStorage.setItem('pomodoroSettings', JSON.stringify(settings));
}

// 設定を適用
function applySettings() {
    // テーマを適用
    document.body.className = settings.theme === 'dark' ? 'dark-theme' : 
                              settings.theme === 'focus' ? 'focus-theme' : '';
    
    // 作業時間ボタンのアクティブ状態を更新
    document.querySelectorAll('.time-btn').forEach(btn => {
        const onclick = btn.getAttribute('onclick');
        if (onclick.includes('setWorkTime')) {
            const time = parseInt(onclick.match(/\d+/)[0]);
            btn.classList.toggle('active', time === settings.workTime);
        } else if (onclick.includes('setBreakTime')) {
            const time = parseInt(onclick.match(/\d+/)[0]);
            btn.classList.toggle('active', time === settings.breakTime);
        }
    });
    
    // テーマボタンのアクティブ状態を更新
    document.querySelectorAll('.theme-btn').forEach(btn => {
        const onclick = btn.getAttribute('onclick');
        const theme = onclick.match(/'(\w+)'/)[1];
        btn.classList.toggle('active', theme === settings.theme);
    });
    
    // サウンド設定のチェックボックスを更新
    document.getElementById('startSound').checked = settings.sounds.start;
    document.getElementById('endSound').checked = settings.sounds.end;
    document.getElementById('tickSound').checked = settings.sounds.tick;
    
    // タイマーをリセット
    if (!isRunning) {
        resetTimer();
    }
}

// 初期化
function init() {
    loadSettings();
    resetTimer();
    
    // セッションカウントを読み込み
    const savedCount = localStorage.getItem('sessionCount');
    if (savedCount) {
        sessionCount = parseInt(savedCount);
        updateSessionCount();
    }
}

// 設定パネルの表示/非表示
function toggleSettings() {
    const content = document.getElementById('settingsContent');
    content.classList.toggle('active');
}

// 作業時間の設定
function setWorkTime(minutes) {
    if (!isRunning) {
        settings.workTime = minutes;
        saveSettings();
        applySettings();
        
        // ボタンのアクティブ状態を更新
        document.querySelectorAll('.time-btn').forEach(btn => {
            const onclick = btn.getAttribute('onclick');
            if (onclick.includes('setWorkTime')) {
                const time = parseInt(onclick.match(/\d+/)[0]);
                btn.classList.toggle('active', time === minutes);
            }
        });
    }
}

// 休憩時間の設定
function setBreakTime(minutes) {
    if (!isRunning) {
        settings.breakTime = minutes;
        saveSettings();
        
        // ボタンのアクティブ状態を更新
        document.querySelectorAll('.time-btn').forEach(btn => {
            const onclick = btn.getAttribute('onclick');
            if (onclick.includes('setBreakTime')) {
                const time = parseInt(onclick.match(/\d+/)[0]);
                btn.classList.toggle('active', time === minutes);
            }
        });
    }
}

// テーマの設定
function setTheme(theme) {
    settings.theme = theme;
    saveSettings();
    applySettings();
    
    // ボタンのアクティブ状態を更新
    document.querySelectorAll('.theme-btn').forEach(btn => {
        const onclick = btn.getAttribute('onclick');
        const btnTheme = onclick.match(/'(\w+)'/)[1];
        btn.classList.toggle('active', btnTheme === theme);
    });
}

// サウンド設定の更新
function updateSoundSettings() {
    settings.sounds.start = document.getElementById('startSound').checked;
    settings.sounds.end = document.getElementById('endSound').checked;
    settings.sounds.tick = document.getElementById('tickSound').checked;
    saveSettings();
}

// タイマーの開始
function startTimer() {
    if (!isRunning) {
        isRunning = true;
        
        // 初回開始時のみ時間を設定
        if (timeLeft === undefined || timeLeft === totalTime) {
            timeLeft = (isWorkSession ? settings.workTime : settings.breakTime) * 60;
            totalTime = timeLeft;
        }
        
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('pauseBtn').style.display = 'inline-block';
        
        playSound('start');
        
        timer = setInterval(() => {
            timeLeft--;
            updateDisplay();
            
            if (settings.sounds.tick && timeLeft % 1 === 0) {
                playSound('tick');
            }
            
            if (timeLeft <= 0) {
                completeSession();
            }
        }, 1000);
    }
}

// タイマーの一時停止
function pauseTimer() {
    if (isRunning) {
        isRunning = false;
        clearInterval(timer);
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('pauseBtn').style.display = 'none';
    }
}

// タイマーのリセット
function resetTimer() {
    isRunning = false;
    clearInterval(timer);
    
    timeLeft = (isWorkSession ? settings.workTime : settings.breakTime) * 60;
    totalTime = timeLeft;
    
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('pauseBtn').style.display = 'none';
    
    updateDisplay();
}

// セッション完了
function completeSession() {
    clearInterval(timer);
    isRunning = false;
    
    playSound('end');
    
    // 通知メッセージを現在のセッション状態に基づいて設定
    const completedWorkSession = isWorkSession;
    
    if (isWorkSession) {
        sessionCount++;
        updateSessionCount();
        localStorage.setItem('sessionCount', sessionCount);
    }
    
    // セッションを切り替え
    isWorkSession = !isWorkSession;
    
    // 次のセッションの時間を設定
    timeLeft = (isWorkSession ? settings.workTime : settings.breakTime) * 60;
    totalTime = timeLeft;
    
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('pauseBtn').style.display = 'none';
    
    updateDisplay();
    
    // 通知
    if (Notification.permission === 'granted') {
        new Notification('ポモドーロタイマー', {
            body: completedWorkSession ? '作業が完了しました。休憩しましょう！' : '休憩が終了しました。作業を開始しましょう！',
            icon: '/static/pomodoro-icon.png'
        });
    }
}

// 表示の更新
function updateDisplay() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    
    document.getElementById('timerTime').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    document.getElementById('timerStatus').textContent = 
        isWorkSession ? '作業セッション' : '休憩中';
    
    // プログレスバーの更新
    const progress = ((totalTime - timeLeft) / totalTime) * 100;
    document.getElementById('progressBar').style.width = `${progress}%`;
}

// セッションカウントの更新
function updateSessionCount() {
    document.getElementById('sessionCount').textContent = sessionCount;
}

// サウンド再生（簡易実装）
function playSound(type) {
    if (!settings.sounds[type]) return;
    
    // AudioContextを初回のみ作成
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    if (type === 'start') {
        oscillator.frequency.value = 440;
        gainNode.gain.value = 0.1;
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.1);
    } else if (type === 'end') {
        oscillator.frequency.value = 880;
        gainNode.gain.value = 0.1;
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.3);
    } else if (type === 'tick') {
        oscillator.frequency.value = 220;
        gainNode.gain.value = 0.02;
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.01);
    }
}

// 通知の許可をリクエスト
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// ページ読み込み時に初期化
window.addEventListener('DOMContentLoaded', init);
