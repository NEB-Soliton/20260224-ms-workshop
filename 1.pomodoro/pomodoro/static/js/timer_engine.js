(function () {
	const STATE = {
		IDLE: "idle",
		RUNNING: "running",
		PAUSED: "paused",
		COMPLETED: "completed",
	};

	const MODE = {
		FOCUS: "focus",
		SHORT_BREAK: "short_break",
		LONG_BREAK: "long_break",
	};

	function createTimerEngine(options = {}) {
		const durations = {
			[MODE.FOCUS]: options.focusSeconds ?? 25 * 60,
			[MODE.SHORT_BREAK]: options.shortBreakSeconds ?? 5 * 60,
			[MODE.LONG_BREAK]: options.longBreakSeconds ?? 15 * 60,
		};

		let mode = options.initialMode ?? MODE.FOCUS;
		let state = STATE.IDLE;
		let totalMs = durations[mode] * 1000;
		let remainingMs = totalMs;
		let targetTimestamp = null;

		function setMode(nextMode) {
			if (!Object.values(MODE).includes(nextMode)) {
				return;
			}

			mode = nextMode;
			reset();
		}

		function start(now = Date.now()) {
			if (state === STATE.RUNNING) {
				return;
			}

			if (state === STATE.IDLE || state === STATE.COMPLETED) {
				totalMs = durations[mode] * 1000;
				remainingMs = totalMs;
			}

			targetTimestamp = now + remainingMs;
			state = STATE.RUNNING;
		}

		function pause(now = Date.now()) {
			if (state !== STATE.RUNNING) {
				return;
			}

			remainingMs = Math.max(0, targetTimestamp - now);
			targetTimestamp = null;
			state = STATE.PAUSED;
		}

		function resume(now = Date.now()) {
			if (state !== STATE.PAUSED) {
				return;
			}

			targetTimestamp = now + remainingMs;
			state = STATE.RUNNING;
		}

		function reset() {
			totalMs = durations[mode] * 1000;
			remainingMs = totalMs;
			targetTimestamp = null;
			state = STATE.IDLE;
		}

		function tick(now = Date.now()) {
			if (state !== STATE.RUNNING) {
				return;
			}

			remainingMs = Math.max(0, targetTimestamp - now);

			if (remainingMs === 0) {
				state = STATE.COMPLETED;
				targetTimestamp = null;
			}
		}

		function getSnapshot() {
			const safeTotal = Math.max(1, totalMs);
			const progress = ((safeTotal - remainingMs) / safeTotal) * 100;

			return {
				mode,
				state,
				remainingMs,
				totalMs,
				progress,
			};
		}

		return {
			STATE,
			MODE,
			setMode,
			start,
			pause,
			resume,
			reset,
			tick,
			getSnapshot,
		};
	}

	window.PomodoroTimerEngine = {
		createTimerEngine,
		STATE,
		MODE,
	};
})();
