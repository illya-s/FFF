$(document).ready(function () {
	let seconds = parseInt($("#countdown").data('sec'));

	function updateTimer() {
		if (seconds <= 0) {
			$('#countdown').text('Скоро запускается...');
			return;
		}

		let h = Math.floor(seconds / 3600);
		let m = Math.floor((seconds % 3600) / 60);
		let s = seconds % 60;

		let formatted = 
			String(h).padStart(2, '0') + ':' + 
			String(m).padStart(2, '0') + ':' + 
			String(s).padStart(2, '0');

		$('#countdown').text(formatted);
		seconds--;
	}

	updateTimer();
	setInterval(updateTimer, 1000);
});