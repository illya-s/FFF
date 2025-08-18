$(document).ready(function () {
	const params = new URLSearchParams(window.location.search);

	const pn = parseInt($('.page-number').data('val'))
	const pageNumber = pn ? pn : 1

	if (!params.has('p') || params.get('p') != pageNumber) {
		params.set('p', pageNumber);
		const newUrl = `${window.location.pathname}?${params.toString()}`;
		history.replaceState(null, '', newUrl);
	}

	$(document).on('click', '.page-link', function () {
		params.set('p', $(this).data("page"));
		window.location.search = params.toString();
	});
});