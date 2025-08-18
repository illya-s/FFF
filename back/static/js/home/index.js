$(document).ready(function () {
	$('.top-genres-cont').owlCarousel({
		margin: 10,
		nav: true,
		navText: [
			`<div class="top-genres-prevArrow"><svg width="21" height="34" viewBox="0 0 21 34" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 31L4 17L18 3" stroke="currentColor" stroke-width="5" stroke-linecap="round"/></svg></div>`,
			`<div class="top-genres-nextArrow"><svg width="21" height="34" viewBox="0 0 21 34" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 3L17 17L3 31" stroke="currentColor" stroke-width="5" stroke-linecap="round"/></svg></div>`
		],
		dots: false,

		responsive:{
			0:{
				items: 3,
				slideBy: 3,
			},
			600:{
				items: 4,
				slideBy: 4,
			},
			1000:{
				items: 5,
				slideBy: 5,
			}
		}
	})

	$('.media-carousel').owlCarousel({
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
				items: 6,
				slideBy: 6,
				nav: false,
				dots: false
			},
			1001: {
				items: 6,
				slideBy: 6,
				nav: true,
				dots: false
			},
			1200: {
				items: 8,
				slideBy: 8,
				nav: true,
				dots: false
			}
		}
	});
});