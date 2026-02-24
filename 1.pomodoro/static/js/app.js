/**
 * Pomodoro Timer Application
 * JSON永続化機能付き
 */

class PomodoroTimer {
    constructor() {
        // 設定
        this.settings = null;
        
        // タイマー状態
        this.isRunning = false;
        this.isPaused = false;
        this.currentTime = 0; // 秒単位
        this.totalTime = 0;
        this.timerInterval = null;
        
        // セッション管理
        this.sessionType = 'work'; // 'work', 'short_break', 'long_break'
        this.pomodoroCount = 0;
        this.currentSessionStart = null;
        
        // DOM要素
        this.timerDisplay = document.getElementById('timerDisplay');
        this.sessionLabel = document.getElementById('sessionLabel');
        this.pomodoroCountDisplay = document.getElementById('pomodoroCount');
        this.progressCircle = document.getElementById('progressCircle');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        
        // 統計表示要素
        this.todayPomodoros = document.getElementById('todayPomodoros');
        this.todayWorkTime = document.getElementById('todayWorkTime');
        this.todayBreakTime = document.getElementById('todayBreakTime');
        
        // プログレスサークルの設定
        this.circleRadius = 120;
        this.circleCircumference = 2 * Math.PI * this.circleRadius;
        this.progressCircle.style.strokeDasharray = this.circleCircumference;
        
        this.init();
    }
    
    async init() {
        // 設定を読み込み
        await this.loadSettings();
        
        // イベントリスナーを設定
        this.setupEventListeners();
        
        // タイマーを初期化
        this.resetTimer();
        
        // 今日の統計を読み込み
        await this.updateTodayStats();
        
        // モーダルの設定
        this.setupModals();
    }
    
    setupEventListeners() {
        this.startBtn.addEventListener('click', () => this.start());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.resetBtn.addEventListener('click', () => this.resetTimer());
        
        // 設定フォーム
        const settingsForm = document.getElementById('settingsForm');
        settingsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });
        
        document.getElementById('resetSettingsBtn').addEventListener('click', () => {
            this.resetSettings();
        });
    }
    
    setupModals() {
        // 統計モーダル
        const statsBtn = document.getElementById('statsBtn');
        const statsModal = document.getElementById('statsModal');
        const settingsBtn = document.getElementById('settingsBtn');
        const settingsModal = document.getElementById('settingsModal');
        
        statsBtn.addEventListener('click', () => {
            this.openStatsModal();
        });
        
        settingsBtn.addEventListener('click', () => {
            this.openSettingsModal();
        });
        
        // 閉じるボタン
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').classList.remove('show');
            });
        });
        
        // モーダルの外側をクリックで閉じる
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('show');
            }
        });
    }
    
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            this.settings = await response.json();
        } catch (error) {
            console.error('設定の読み込みに失敗しました:', error);
            // デフォルト設定を使用
            this.settings = {
                work_duration: 25,
                short_break_duration: 5,
                long_break_duration: 15,
                pomodoros_until_long_break: 4,
                auto_start_breaks: false,
                auto_start_pomodoros: false,
                sound_enabled: true,
                sound_volume: 0.7
            };
        }
    }
    
    async saveSettings() {
        const newSettings = {
            work_duration: parseInt(document.getElementById('workDuration').value),
            short_break_duration: parseInt(document.getElementById('shortBreakDuration').value),
            long_break_duration: parseInt(document.getElementById('longBreakDuration').value),
            pomodoros_until_long_break: parseInt(document.getElementById('pomodorosUntilLongBreak').value),
            auto_start_breaks: document.getElementById('autoStartBreaks').checked,
            auto_start_pomodoros: document.getElementById('autoStartPomodoros').checked,
            sound_enabled: document.getElementById('soundEnabled').checked,
            sound_volume: parseFloat(document.getElementById('soundVolume').value)
        };
        
        try {
            const response = await fetch('/api/settings', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newSettings)
            });
            
            this.settings = await response.json();
            this.resetTimer();
            document.getElementById('settingsModal').classList.remove('show');
            alert('設定を保存しました');
        } catch (error) {
            console.error('設定の保存に失敗しました:', error);
            alert('設定の保存に失敗しました');
        }
    }
    
    async resetSettings() {
        if (!confirm('設定をデフォルトに戻しますか？')) {
            return;
        }
        
        try {
            const response = await fetch('/api/settings/reset', {
                method: 'POST'
            });
            this.settings = await response.json();
            this.populateSettingsForm();
            this.resetTimer();
            alert('設定をリセットしました');
        } catch (error) {
            console.error('設定のリセットに失敗しました:', error);
            alert('設定のリセットに失敗しました');
        }
    }
    
    openSettingsModal() {
        this.populateSettingsForm();
        document.getElementById('settingsModal').classList.add('show');
    }
    
    populateSettingsForm() {
        document.getElementById('workDuration').value = this.settings.work_duration;
        document.getElementById('shortBreakDuration').value = this.settings.short_break_duration;
        document.getElementById('longBreakDuration').value = this.settings.long_break_duration;
        document.getElementById('pomodorosUntilLongBreak').value = this.settings.pomodoros_until_long_break;
        document.getElementById('autoStartBreaks').checked = this.settings.auto_start_breaks;
        document.getElementById('autoStartPomodoros').checked = this.settings.auto_start_pomodoros;
        document.getElementById('soundEnabled').checked = this.settings.sound_enabled;
        document.getElementById('soundVolume').value = this.settings.sound_volume;
    }
    
    async openStatsModal() {
        document.getElementById('statsModal').classList.add('show');
        await this.loadStatsData();
    }
    
    async loadStatsData() {
        try {
            // 今週の統計
            const weekResponse = await fetch('/api/stats/week');
            const weekStats = await weekResponse.json();
            this.displayWeekStats(weekStats);
            
            // 過去7日間の統計
            const historyResponse = await fetch('/api/stats/history?days=7');
            const historyStats = await historyResponse.json();
            this.displayHistoryStats(historyStats);
        } catch (error) {
            console.error('統計情報の読み込みに失敗しました:', error);
        }
    }
    
    displayWeekStats(stats) {
        const weekStatsDiv = document.getElementById('weekStats');
        weekStatsDiv.innerHTML = `
            <p><strong>完了したポモドーロ:</strong> ${stats.completed_pomodoros}</p>
            <p><strong>総作業時間:</strong> ${stats.total_work_time_hours}時間</p>
            <p><strong>総休憩時間:</strong> ${stats.total_break_time_minutes}分</p>
            <p><strong>平均作業時間:</strong> ${stats.average_duration_minutes}分</p>
            <p><strong>総セッション数:</strong> ${stats.total_sessions}</p>
        `;
    }
    
    displayHistoryStats(history) {
        const historyDiv = document.getElementById('historyStats');
        historyDiv.innerHTML = '';
        
        history.forEach(day => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `
                <div class="history-date">${day.date}</div>
                <div class="history-stats">
                    <span>🍅 ${day.completed_pomodoros}</span>
                    <span>⏱️ ${day.total_work_time_hours}h</span>
                </div>
            `;
            historyDiv.appendChild(item);
        });
    }
    
    async updateTodayStats() {
        try {
            const response = await fetch('/api/stats/today');
            const stats = await response.json();
            
            this.todayPomodoros.textContent = stats.completed_pomodoros;
            this.todayWorkTime.textContent = stats.total_work_time_hours + 'h';
            this.todayBreakTime.textContent = stats.total_break_time_minutes + 'm';
        } catch (error) {
            console.error('統計情報の更新に失敗しました:', error);
        }
    }
    
    start() {
        if (this.isRunning && !this.isPaused) {
            return;
        }
        
        if (!this.isPaused) {
            // 新しいセッション開始
            this.currentSessionStart = new Date().toISOString();
        }
        
        this.isRunning = true;
        this.isPaused = false;
        this.startBtn.style.display = 'none';
        this.pauseBtn.style.display = 'inline-block';
        
        this.timerInterval = setInterval(() => {
            this.tick();
        }, 1000);
    }
    
    pause() {
        this.isPaused = true;
        this.isRunning = false;
        this.startBtn.style.display = 'inline-block';
        this.pauseBtn.style.display = 'none';
        clearInterval(this.timerInterval);
    }
    
    tick() {
        this.currentTime--;
        
        if (this.currentTime <= 0) {
            this.completeSession();
        }
        
        this.updateDisplay();
    }
    
    async completeSession() {
        clearInterval(this.timerInterval);
        this.isRunning = false;
        
        // セッションを保存
        await this.saveSession();
        
        // 通知音を再生
        this.playNotificationSound();
        
        // 次のセッションに移行
        this.moveToNextSession();
    }
    
    async saveSession() {
        const endTime = new Date().toISOString();
        const duration = Math.round((new Date(endTime) - new Date(this.currentSessionStart)) / 60000);
        
        const session = {
            start_time: this.currentSessionStart,
            end_time: endTime,
            duration: duration,
            session_type: this.sessionType,
            completed: true
        };
        
        try {
            await fetch('/api/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(session)
            });
            
            // 統計を更新
            await this.updateTodayStats();
        } catch (error) {
            console.error('セッションの保存に失敗しました:', error);
        }
    }
    
    moveToNextSession() {
        if (this.sessionType === 'work') {
            this.pomodoroCount++;
            
            // 長い休憩か短い休憩か判定
            if (this.pomodoroCount % this.settings.pomodoros_until_long_break === 0) {
                this.sessionType = 'long_break';
            } else {
                this.sessionType = 'short_break';
            }
            
            // 自動開始が有効なら開始
            if (this.settings.auto_start_breaks) {
                this.resetTimer();
                setTimeout(() => this.start(), 1000);
            } else {
                this.resetTimer();
            }
        } else {
            this.sessionType = 'work';
            
            if (this.settings.auto_start_pomodoros) {
                this.resetTimer();
                setTimeout(() => this.start(), 1000);
            } else {
                this.resetTimer();
            }
        }
    }
    
    resetTimer() {
        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.isPaused = false;
        this.startBtn.style.display = 'inline-block';
        this.pauseBtn.style.display = 'none';
        
        // セッションタイプに応じた時間を設定
        if (this.sessionType === 'work') {
            this.totalTime = this.settings.work_duration * 60;
            this.sessionLabel.textContent = '作業時間';
            this.progressCircle.style.stroke = '#667eea';
        } else if (this.sessionType === 'short_break') {
            this.totalTime = this.settings.short_break_duration * 60;
            this.sessionLabel.textContent = '短い休憩';
            this.progressCircle.style.stroke = '#48bb78';
        } else {
            this.totalTime = this.settings.long_break_duration * 60;
            this.sessionLabel.textContent = '長い休憩';
            this.progressCircle.style.stroke = '#38b2ac';
        }
        
        this.currentTime = this.totalTime;
        this.updateDisplay();
    }
    
    updateDisplay() {
        // 時間表示
        const minutes = Math.floor(this.currentTime / 60);
        const seconds = this.currentTime % 60;
        this.timerDisplay.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // ポモドーロカウント
        this.pomodoroCountDisplay.textContent = 
            `${this.pomodoroCount} / ${this.settings.pomodoros_until_long_break}`;
        
        // プログレスサークル
        const progress = (this.totalTime - this.currentTime) / this.totalTime;
        const offset = this.circleCircumference * (1 - progress);
        this.progressCircle.style.strokeDashoffset = offset;
    }
    
    playNotificationSound() {
        if (!this.settings.sound_enabled) {
            return;
        }
        
        // Web Audio APIで通知音を生成
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        gainNode.gain.value = this.settings.sound_volume;
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.2);
        
        // 2回目のビープ
        setTimeout(() => {
            const osc2 = audioContext.createOscillator();
            const gain2 = audioContext.createGain();
            osc2.connect(gain2);
            gain2.connect(audioContext.destination);
            osc2.frequency.value = 800;
            osc2.type = 'sine';
            gain2.gain.value = this.settings.sound_volume;
            osc2.start();
            osc2.stop(audioContext.currentTime + 0.2);
        }, 300);
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});
