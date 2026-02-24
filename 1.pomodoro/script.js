// ポモドーロタイマー - 視覚的フィードバック強化版

// 定数定義
const NOTIFICATION_FREQUENCY_HZ = 800; // 通知音の周波数（Hz）
const NOTIFICATION_VOLUME = 0.3; // 通知音のボリューム（0.0-1.0）

class PomodoroTimer {
    constructor() {
        // DOM要素
        this.timeDisplay = document.getElementById('timeDisplay');
        this.sessionType = document.getElementById('sessionType');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.workDurationInput = document.getElementById('workDuration');
        this.breakDurationInput = document.getElementById('breakDuration');
        this.completedSessionsDisplay = document.getElementById('completedSessions');
        this.progressCircle = document.getElementById('progressCircle');
        this.gradientStart = document.getElementById('gradientStart');
        this.gradientEnd = document.getElementById('gradientEnd');
        this.particlesBackground = document.getElementById('particlesBackground');
        this.rippleContainer = document.getElementById('rippleContainer');
        
        // プログレスリングの設定
        this.radius = 130;
        this.circumference = 2 * Math.PI * this.radius;
        this.progressCircle.style.strokeDasharray = `${this.circumference} ${this.circumference}`;
        this.progressCircle.style.strokeDashoffset = 0;
        
        // タイマー状態
        this.isRunning = false;
        this.isWorkSession = true;
        this.timeLeft = 0;
        this.totalTime = 0;
        this.timerInterval = null;
        this.completedSessions = 0;
        
        // エフェクト制御
        this.particleInterval = null;
        this.rippleInterval = null;
        
        // イベントリスナー
        this.startBtn.addEventListener('click', () => this.start());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.resetBtn.addEventListener('click', () => this.reset());
        
        // 初期化
        this.reset();
    }
    
    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.startBtn.disabled = true;
            this.pauseBtn.disabled = false;
            this.workDurationInput.disabled = true;
            this.breakDurationInput.disabled = true;
            
            // タイマー開始
            this.timerInterval = setInterval(() => this.tick(), 1000);
            
            // 作業セッション時のエフェクト開始
            if (this.isWorkSession) {
                this.startParticles();
                this.startRipples();
            }
        }
    }
    
    pause() {
        if (this.isRunning) {
            this.isRunning = false;
            this.startBtn.disabled = false;
            this.pauseBtn.disabled = true;
            
            clearInterval(this.timerInterval);
            this.stopParticles();
            this.stopRipples();
        }
    }
    
    reset() {
        this.pause();
        
        const workDuration = parseInt(this.workDurationInput.value) || 25;
        const breakDuration = parseInt(this.breakDurationInput.value) || 5;
        
        this.isWorkSession = true;
        this.timeLeft = workDuration * 60;
        this.totalTime = workDuration * 60;
        
        this.workDurationInput.disabled = false;
        this.breakDurationInput.disabled = false;
        this.startBtn.disabled = false;
        
        this.updateDisplay();
        this.updateProgress();
        this.updateColors(1.0);
        this.sessionType.textContent = '作業時間';
    }
    
    tick() {
        this.timeLeft--;
        
        if (this.timeLeft <= 0) {
            this.onSessionComplete();
        } else {
            this.updateDisplay();
            this.updateProgress();
            
            // 色のグラデーション更新
            const progress = this.timeLeft / this.totalTime;
            this.updateColors(progress);
        }
    }
    
    onSessionComplete() {
        // セッション完了通知
        this.playNotification();
        
        if (this.isWorkSession) {
            this.completedSessions++;
            this.completedSessionsDisplay.textContent = this.completedSessions;
            
            // 休憩セッションに切り替え
            this.isWorkSession = false;
            const breakDuration = parseInt(this.breakDurationInput.value) || 5;
            this.timeLeft = breakDuration * 60;
            this.totalTime = breakDuration * 60;
            this.sessionType.textContent = '休憩時間';
            
            // エフェクト停止
            this.stopParticles();
            this.stopRipples();
        } else {
            // 作業セッションに戻る
            this.isWorkSession = true;
            const workDuration = parseInt(this.workDurationInput.value) || 25;
            this.timeLeft = workDuration * 60;
            this.totalTime = workDuration * 60;
            this.sessionType.textContent = '作業時間';
            
            // エフェクト開始
            this.startParticles();
            this.startRipples();
        }
        
        this.updateDisplay();
        this.updateProgress();
        this.updateColors(1.0);
    }
    
    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        this.timeDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    updateProgress() {
        const progress = this.timeLeft / this.totalTime;
        const offset = this.circumference * (1 - progress);
        this.progressCircle.style.strokeDashoffset = offset;
    }
    
    // 色のグラデーション変化: 青 → 黄 → 赤
    updateColors(progress) {
        let startColor, endColor, textColor;
        
        if (progress > 0.5) {
            // 青 → 黄 (progress: 1.0 -> 0.5)
            const localProgress = (progress - 0.5) * 2; // 0.0 -> 1.0
            startColor = this.interpolateColor('#4A90E2', '#F39C12', 1 - localProgress);
            endColor = this.interpolateColor('#5DADE2', '#F7B731', 1 - localProgress);
            textColor = this.interpolateColor('#4A90E2', '#F39C12', 1 - localProgress);
        } else {
            // 黄 → 赤 (progress: 0.5 -> 0.0)
            const localProgress = progress * 2; // 0.0 -> 1.0
            startColor = this.interpolateColor('#F39C12', '#E74C3C', 1 - localProgress);
            endColor = this.interpolateColor('#F7B731', '#EC7063', 1 - localProgress);
            textColor = this.interpolateColor('#F39C12', '#E74C3C', 1 - localProgress);
        }
        
        this.gradientStart.style.stopColor = startColor;
        this.gradientEnd.style.stopColor = endColor;
        this.timeDisplay.style.color = textColor;
    }
    
    // 2色間の補間
    interpolateColor(color1, color2, factor) {
        const c1 = this.hexToRgb(color1);
        const c2 = this.hexToRgb(color2);
        
        const r = Math.round(c1.r + factor * (c2.r - c1.r));
        const g = Math.round(c1.g + factor * (c2.g - c1.g));
        const b = Math.round(c1.b + factor * (c2.b - c1.b));
        
        return this.rgbToHex(r, g, b);
    }
    
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : { r: 0, g: 0, b: 0 };
    }
    
    rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }
    
    // パーティクルエフェクト開始
    startParticles() {
        this.stopParticles(); // 既存のパーティクルを停止
        
        this.particleInterval = setInterval(() => {
            this.createParticle();
        }, 300);
    }
    
    stopParticles() {
        if (this.particleInterval) {
            clearInterval(this.particleInterval);
            this.particleInterval = null;
        }
    }
    
    createParticle() {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        const particleSize = Math.random() * 5 + 2;
        const startX = Math.random() * window.innerWidth;
        const drift = (Math.random() - 0.5) * 100;
        const duration = Math.random() * 5 + 5;
        
        particle.style.width = `${particleSize}px`;
        particle.style.height = `${particleSize}px`;
        particle.style.left = `${startX}px`;
        particle.style.bottom = '0';
        particle.style.setProperty('--drift', `${drift}px`);
        particle.style.animationDuration = `${duration}s`;
        
        this.particlesBackground.appendChild(particle);
        
        // アニメーション終了後に削除
        setTimeout(() => {
            particle.remove();
        }, duration * 1000);
    }
    
    // 波紋エフェクト開始
    startRipples() {
        this.stopRipples(); // 既存の波紋を停止
        
        this.rippleInterval = setInterval(() => {
            this.createRipple();
        }, 2000);
    }
    
    stopRipples() {
        if (this.rippleInterval) {
            clearInterval(this.rippleInterval);
            this.rippleInterval = null;
        }
    }
    
    createRipple() {
        const ripple = document.createElement('div');
        ripple.className = 'ripple';
        
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * window.innerHeight;
        
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        this.rippleContainer.appendChild(ripple);
        
        // アニメーション終了後に削除
        setTimeout(() => {
            ripple.remove();
        }, 3000);
    }
    
    // 通知音（簡易的なビープ音）
    playNotification() {
        // Web Audio APIを使用した簡易ビープ音
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = NOTIFICATION_FREQUENCY_HZ;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(NOTIFICATION_VOLUME, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (e) {
            console.log('Audio notification not available');
        }
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});
