(function () {
	function init() {
		const elements = {
			modeLabel: document.getElementById("modeLabel"),
			timeDisplay: document.getElementById("timeDisplay"),
			progressRing: document.getElementById("progressRing"),
			primaryButton: document.getElementById("primaryButton"),
			resetButton: document.getElementById("resetButton"),
		};

		const engine = window.PomodoroTimerEngine.createTimerEngine({
			initialMode: window.PomodoroTimerEngine.MODE.FOCUS,
		});
		const ui = window.PomodoroUI.createTimerUI(elements);

		let intervalId = null;

		function stopLoop() {
			if (intervalId !== null) {
				clearInterval(intervalId);
				intervalId = null;
			}
		}

		function updateView() {
			ui.render(engine.getSnapshot());
		}

		function ensureLoop() {
			if (intervalId !== null) {
				return;
			}

			intervalId = setInterval(function () {
				engine.tick();
				const snapshot = engine.getSnapshot();
				ui.render(snapshot);

				if (snapshot.state !== window.PomodoroTimerEngine.STATE.RUNNING) {
					stopLoop();
				}
			}, 250);
		}

		elements.primaryButton.addEventListener("click", function () {
			const state = engine.getSnapshot().state;

			if (state === window.PomodoroTimerEngine.STATE.RUNNING) {
				engine.pause();
				stopLoop();
			} else if (state === window.PomodoroTimerEngine.STATE.PAUSED) {
				engine.resume();
				ensureLoop();
			} else {
				engine.start();
				ensureLoop();
			}

			updateView();
		});

		elements.resetButton.addEventListener("click", function () {
			engine.reset();
			stopLoop();
			updateView();
		});

		updateView();
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
