$(document).ready(function () {
	// const firstVideo = $($(".video-btn")[0]);
	// firstVideo.addClass('active');


	// const voiceoverSelect = $('#mediaVoiceoverSelect')
	// const voiceovers = window.voiceovers()
	// for (let index = 0; index < voiceovers.length; index++) {
	// 	const element = voiceovers[index];
		
	// 	var el = $('<option>', {
	// 		value: element['id']
	// 	}).text(element['name'])
	// 	voiceoverSelect.append(el)
	// }

	

	// data = []
	// voiceovers.forEach(element => {
	// 	data.push({
	// 		id: String(element.id),
	// 		name: element.name,
	// 		list: element.videos.map(video => video.url)
	// 	})
	// });

	// window.player = new MVideo('#player');
	// window.player.switchControls.loadData(data);
	// window.player._videoWrapper.focus();

	// var player = new Playerjs({
	// 	id: "player",
	// 	file: firstVideo.data('url')
	// });

	// $(".video-btn").on("click", function () {
	// 	$(".video-btn").each(function (i, element) {
	// 		$(this).removeClass('active');
	// 	});
	// 	$(this).addClass('active');

	// 	var newFile = $(this).data('url');
	// 	player.api("file", newFile);
	// });

	// $('.media-btns').hide()

	function fadeToggleFlex($el, duration = 300) {
		if ($el.css('display') === 'none') {
			$el.css({ display: 'flex', opacity: 0 }).fadeTo(duration, 1);
		} else {
			$el.fadeTo(duration, 0, function() {
				$el.hide();
			});
		}
	}

	$(".media-add-to-btn").on('click', () => {
		$('.media-add-to-wrapper').toggleClass('active')
		fadeToggleFlex($('.media-btns'), 200)
	})

	$('.media-btn-checkbox').on('change', function (e) {
		const is_checked = $(this).is(':checked');
		const btn_type = $(this).data('type')
		
		$(this).addClass('load')

		$.ajax({
			type: "POST",
			url: $('meta[name="toggleUserListUrl"]').attr('content'),
			data: {'type': btn_type, 'is_add': is_checked},
			dataType: "dataType",
			success: function (response) {
				console.log(response.message)
			}
		});
		$(this).removeClass('load')
	});
});