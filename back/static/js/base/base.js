$(document).ready(function () {
	const page_name = $('meta[name="page_name"]').attr('content');

	$.ajax({
		type: "GET",
		url: $('#asideRandom').data('url'),
		success: function (response) {
			const title = $('<span>').text('Случайная дорама')
			const link = $('<a>', {
				class: 'aside-link',
				href: response.url,
				title: 'Случайный фильм / сериал'
			}).html(window.svgRandom)
			link.append(title)
			$('#asideRandom').html(link)

			const hlink = $('<a>', {
			    class: 'header-mobile-random-media-link',
			    href: response.url,
			    title: 'Случайный фильм / сериал'
			}).html(window.svgRandom)
			$('#headerMobileRandom').html(hlink)
		}
	});


	$.ajax({
		type: "GET",
		url: $('#asideCommunity').data('url'),
		success: function (response) {
			$.each(response.socials, function(i, social) {
				const link = $('<a>', {
					class: "aside-link",
					title: social.name,
					href: social.url,
					target: "_blank"
				})

				link.html(social.icon_svg)
				link.append($('<span>').text(social.name))
				$('#asideCommunity').append(link)
			});
		}
	})


	$('.header-logo-mobile, #hideAside').on('click', function () {
		$('.aside').toggleClass('active');
	})

	$('.search-mobile').on('click', function () {
		$('.search-cont').addClass('active');
		$('.search-input').focus()
	})
	$('.search-back').on('click', function() {
		$('.search-cont').removeClass('active');
	});
	$('.header-profile-toggle').on('click', function () {
		$('.dropdown-content').toggleClass('active');
	})
	$(document).on('click', function(e) {
		if (!$(e.target).closest('.header-logo-mobile, .header-links').length) {
			$('.header-links').removeClass('active');
		}
		if (!$(e.target).closest('.search-mobile, .search-cont').length) {
			$('.search-autocomplete').removeClass('active');
		}
		if (!$(e.target).closest('.header-profile-toggle, .dropdown-content').length) {
			$('.dropdown-content').removeClass('active');
		}
	});


	$('.search-autocomplete').on('wheel', function(e) {
		const deltaY = e.originalEvent.deltaY;
		const scrollTop = this.scrollTop;
		const scrollHeight = this.scrollHeight;
		const height = $(this).outerHeight();

		const atTop = scrollTop === 0;
		const atBottom = scrollTop + height >= scrollHeight - 1;

		if ((deltaY < 0 && atTop) || (deltaY > 0 && atBottom)) {
			e.preventDefault(); // блокируем прокрутку страницы
		}
	});


	const headerSearch = $('.header-search');
	const searchAutocomplete = $('.search-autocomplete');
	const searchInput = headerSearch.find('.search-input');
	const searchBtn = headerSearch.find('.search-btn');

	const searchUrl = headerSearch.data('url');
	const autocompleteUrl = searchAutocomplete.data('url');

	function runSearch() {
		const query = searchInput.val().trim();
		console.log('Поисковый запрос:', query);
	
		if (query) {
			window.location.href = `${searchUrl}?q=${encodeURIComponent(query)}`;
		}
	}

	searchBtn.on('click', function(e) {
		e.preventDefault();
		runSearch();
	});

	searchInput.on('keypress', function(e) {
		if (e.which === 13) {
			e.preventDefault();
			runSearch();
		}
	});

	searchInput.on('focus', function (e) {
		const query = $(this).val().trim();

		if (query.length > 2) {
			searchAutocomplete.addClass('active')
		}
	})

	searchInput.on('input', function (e) {
		const query = $(this).val().trim();

		if (query.length > 2) {
			$.ajax({
				type: "GET",
				url: autocompleteUrl,
				data: {"q": query},
				success: function (response) {
					searchAutocomplete.html(response.list)
					searchAutocomplete.addClass('active')
				}
			});
		} else {
			searchAutocomplete.removeClass('active')
		}
	});

	$(document).on('click', function(e) {
		if (!$(e.target).closest('.search-cont, .search-autocomplete, .search-mobile').length) {
			confirmPopupWraper.removeClass('active');
		}
	});


	$('.top_10-list').owlCarousel({
		loop: true,
		margin: 10,

		autoplay: true,
		autoplayTimeout: 5000,
		smartSpeed: 100,
		dots: false,

		nav: true,
		navText: [
			`<div class="prevArrow"><svg width="21" height="34" viewBox="0 0 21 34" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 31L4 17L18 3" stroke="currentColor" stroke-width="5" stroke-linecap="round"/></svg></div>`,
			`<div class="nextArrow"><svg width="21" height="34" viewBox="0 0 21 34" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 3L17 17L3 31" stroke="currentColor" stroke-width="5" stroke-linecap="round"/></svg></div>`
		],
		responsive: {
			0: {
				items: 2,
				slideBy: 2,
				nav: false,
				dots: false,
			},
			341: {
				items: 3,
				slideBy: 3,
				nav: false,
				dots: false,
			},
			481: {
				items: 4,
				slideBy: 4,
				nav: false,
				dots: false
			},
			662: {
				items: 6,
				slideBy: 6,
				nav: false,
				dots: false
			},
			901: {
				items: 2,
				slideBy: 2,
				nav: false,
				dots: false
			},
			1001: {
				items: 2,
				slideBy: 2,
				nav: true,
				dots: false
			},
			1200: {
				items: 2,
				slideBy: 2,
				nav: true,
				dots: false
			}
		}
	});


	const confirmPopupWraper = $("#confirmPopupWraper");
	const confirmMessage = $("#confirmMessage");
	const confirmOk = $("#confirmOk");
	const confirmNo = $("#confirmNo");

	window.confirmation = function (message) {
		return new Promise((resolve) => {
			confirmPopupWraper.addClass("active");

			if (message) {
				confirmMessage.text(message)
			}

			confirmPopupWraper.on('click', function (e) {
				if (e.target === this) {
					confirmNo.click();
				}
			});
			confirmOk.on('click', function (e) {
				confirmPopupWraper.removeClass("active");
				resolve(true);
			})
			confirmNo.on('click', function (e) {
				confirmPopupWraper.removeClass("active");
				resolve(false);
			})
		});
	};
});