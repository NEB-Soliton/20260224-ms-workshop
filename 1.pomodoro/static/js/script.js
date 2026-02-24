/**
 * Pomodoro Timer - Phase 5: JSON永続化対応
 */

class PomodoroTimer {
    constructor() {
        // タイマー状態
        this.timeLeft = 25 * 60; // 秒単位
        this.isRunning = false;
        this.isPaused = false;
        this.timerInterval = null;
        this.sessionType = 'work'; // 'work' or 'break'
        this.sessionStartTime = null;
        
        // 設定
        this.settings = {
            work_duration: 25,
            short_break: 5,
            long_break: 15,
            theme: 'light',
            sound_enabled: true
        };
        
        // DOM要素
        this.timeDisplay = document.getElementById('timeDisplay');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.progressRingCircle = document.querySelector('.progress-ring-circle');
        
        // 円形プログレスバーの設定
        this.radius = 90;
        this.circumference = 2 * Math.PI * this.radius;
        this.progressRingCircle.style.strokeDasharray = this.circumference;
        this.progressRingCircle.style.strokeDashoffset = 0;
        
        // イベントリスナーを設定
        this.initEventListeners();
        
        // 初期化
        this.loadSettings();
        this.loadTodayProgress();
        this.loadHistory();
    }
    
    initEventListeners() {
        this.startBtn.addEventListener('click', () => this.start());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.resetBtn.addEventListener('click', () => this.reset());
        
        // 設定保存ボタン
        document.getElementById('saveSettingsBtn').addEventListener('click', () => this.saveSettings());
        
        // 設定変更時のテーマ適用
        document.getElementById('theme').addEventListener('change', (e) => {
            this.applyTheme(e.target.value);
        });
    }
    
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const settings = await response.json();
            this.settings = settings;
            
            // UIに反映
            document.getElementById('workDuration').value = settings.work_duration;
            document.getElementById('shortBreak').value = settings.short_break;
            document.getElementById('longBreak').value = settings.long_break;
            document.getElementById('theme').value = settings.theme;
            document.getElementById('soundEnabled').checked = settings.sound_enabled;
            
            // テーマを適用
            this.applyTheme(settings.theme);
            
            // タイマーをリセット
            this.timeLeft = settings.work_duration * 60;
            this.updateDisplay();
        } catch (error) {
            console.error('設定の読み込みに失敗:', error);
        }
    }
    
    async saveSettings() {
        const newSettings = {
            work_duration: parseInt(document.getElementById('workDuration').value),
            short_break: parseInt(document.getElementById('shortBreak').value),
            long_break: parseInt(document.getElementById('longBreak').value),
            theme: document.getElementById('theme').value,
            sound_enabled: document.getElementById('soundEnabled').checked
        };
        
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newSettings)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.settings = result.settings;
                alert('設定を保存しました！');
                
                // タイマーをリセット
                this.reset();
            }
        } catch (error) {
            console.error('設定の保存に失敗:', error);
            alert('設定の保存に失敗しました');
        }
    }
    
    applyTheme(theme) {
        document.body.className = `theme-${theme}`;
    }
    
    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.isPaused = false;
            this.sessionStartTime = new Date().toISOString();
            
            this.startBtn.disabled = true;
            this.pauseBtn.disabled = false;
            
            this.timerInterval = setInterval(() => {
                this.tick();
            }, 1000);
        }
    }
    
    pause() {
        if (this.isRunning && !this.isPaused) {
            this.isPaused = true;
            clearInterval(this.timerInterval);
            this.startBtn.disabled = false;
            this.pauseBtn.disabled = true;
        }
    }
    
    reset() {
        this.isRunning = false;
        this.isPaused = false;
        clearInterval(this.timerInterval);
        
        this.timeLeft = this.settings.work_duration * 60;
        this.sessionType = 'work';
        this.sessionStartTime = null;
        
        this.startBtn.disabled = false;
        this.pauseBtn.disabled = true;
        
        this.updateDisplay();
    }
    
    tick() {
        this.timeLeft--;
        this.updateDisplay();
        
        if (this.timeLeft <= 0) {
            this.complete();
        }
    }
    
    async complete() {
        clearInterval(this.timerInterval);
        this.isRunning = false;
        
        // サウンド再生
        if (this.settings.sound_enabled) {
            this.playNotification();
        }
        
        // セッションを履歴に保存
        const sessionData = {
            start_time: this.sessionStartTime,
            end_time: new Date().toISOString(),
            duration: this.sessionType === 'work' ? this.settings.work_duration : this.settings.short_break,
            session_type: this.sessionType,
            completed: true
        };
        
        try {
            await fetch('/api/history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sessionData)
            });
            
            // 進捗と履歴を更新
            await this.loadTodayProgress();
            await this.loadHistory();
        } catch (error) {
            console.error('セッションの保存に失敗:', error);
        }
        
        // 次のセッションの準備
        if (this.sessionType === 'work') {
            alert('作業完了！休憩時間です🎉');
            this.sessionType = 'break';
            this.timeLeft = this.settings.short_break * 60;
        } else {
            alert('休憩完了！次の作業に取り掛かりましょう💪');
            this.sessionType = 'work';
            this.timeLeft = this.settings.work_duration * 60;
        }
        
        this.startBtn.disabled = false;
        this.pauseBtn.disabled = true;
        this.updateDisplay();
    }
    
    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        this.timeDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // 進捗リングを更新
        const totalTime = (this.sessionType === 'work' ? this.settings.work_duration : this.settings.short_break) * 60;
        const progress = (totalTime - this.timeLeft) / totalTime;
        const offset = this.circumference * (1 - progress);
        this.progressRingCircle.style.strokeDashoffset = offset;
    }
    
    async loadTodayProgress() {
        try {
            const response = await fetch('/api/progress/today');
            const progress = await response.json();
            
            document.getElementById('todaySessions').textContent = progress.completed_sessions;
            document.getElementById('todayWorkTime').textContent = progress.total_work_time;
            document.getElementById('todayBreakTime').textContent = progress.total_break_time;
        } catch (error) {
            console.error('進捗の読み込みに失敗:', error);
        }
    }
    
    async loadHistory() {
        try {
            const response = await fetch('/api/history?limit=5');
            const sessions = await response.json();
            
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';
            
            if (sessions.length === 0) {
                historyList.innerHTML = '<p style="color: #999; text-align: center;">履歴がありません</p>';
                return;
            }
            
            sessions.forEach(session => {
                const item = document.createElement('div');
                item.className = `history-item ${session.session_type}`;
                
                const startTime = new Date(session.start_time);
                const timeStr = startTime.toLocaleString('ja-JP', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                const typeLabel = session.session_type === 'work' ? '作業' : '休憩';
                const emoji = session.session_type === 'work' ? '🍅' : '☕';
                
                item.innerHTML = `
                    <div class="history-time">${timeStr}</div>
                    <div class="history-details">${emoji} ${typeLabel} (${session.duration}分)</div>
                `;
                
                historyList.appendChild(item);
            });
        } catch (error) {
            console.error('履歴の読み込みに失敗:', error);
        }
    }
    
    playNotification() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.error('通知音の再生に失敗:', error);
        }
    }
}

// DOMContentLoadedイベントでタイマーを初期化
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});
