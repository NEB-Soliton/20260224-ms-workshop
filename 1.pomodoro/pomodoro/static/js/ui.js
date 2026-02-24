(function () {
	const modeLabelMap = {
		focus: "作業中",
		short_break: "短い休憩",
		long_break: "長い休憩",
	};

	function formatRemaining(remainingMs) {
		const totalSeconds = Math.max(0, Math.ceil(remainingMs / 1000));
		const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
		const seconds = String(totalSeconds % 60).padStart(2, "0");
		return `${minutes}:${seconds}`;
	}

	function createTimerUI(elements) {
		function render(snapshot) {
			elements.timeDisplay.textContent = formatRemaining(snapshot.remainingMs);
			elements.modeLabel.textContent = modeLabelMap[snapshot.mode] ?? "作業中";
			elements.progressRing.style.setProperty(
				"--progress",
				String(Math.min(100, Math.max(0, snapshot.progress)))
			);

			if (snapshot.state === "running") {
				elements.primaryButton.textContent = "一時停止";
			} else if (snapshot.state === "paused") {
				elements.primaryButton.textContent = "再開";
			} else {
				elements.primaryButton.textContent = "開始";
			}
		}

		return {
			render,
		};
	}

	window.PomodoroUI = {
		createTimerUI,
	};
})();
