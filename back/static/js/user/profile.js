$(document).ready(function () {
	const uploadUserAvatar = $('#id_avatar');
	const saveAvatarBtn = $('.save-avatar');

	const userLogoCont = $('.user-logo');
	const userLogoImg = $(userLogoCont.find('img')) || $('.user-first-logo')
	// try {
		
	// } catch (error) {
	// 	const userLogoImg = 
	// }


	uploadUserAvatar.on('change', function () {
		const file = this.files[0];

		if (file && !file.type.startsWith('image/')) {
			alert('Выберите картинку!')
			return;
		}

		const reader = new FileReader();
		reader.onload = function(e) {
			const img = new Image();
			img.onload = function () {
				const width = img.width; const height = img.height;
				const ratio = (width / height).toFixed(2);

				if (ratio == 1) {
					userLogoCont.html(
						$('<img>', {
							src: e.target.result,
							alt: "Аватар"
						})
					)
					saveAvatarBtn.removeAttr('disabled');
					saveAvatarBtn.addClass('active');
				} else {
					alert('Картинка должна быть квадратом!')
					return;
				}
			};
			img.src = e.target.result;
		};
		reader.readAsDataURL(file);
	})
});