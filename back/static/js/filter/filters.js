$(document).ready(function () {
	// if (!params.has('order_by')) {
	// 	params.set('order_by', order_by);
	// 	const newUrl = `${window.location.pathname}?${params.toString()}`;
	// 	history.replaceState(null, '', newUrl);
	// }

	$('.year-select').mSelect("Все года");
	$('.countries-select').mSelect("Все страны");
	$('.genres-select').mSelect("Все жанры");
	$('.genres-exclude-select').mSelect("Не выбрано");


	// const cVal = $('.chapter-select').find('option[data-checked=""]')[0].value
	// $('.chapter-select').val(cVal)

	const SOrderBy = sessionStorage.getItem('order_by');
	if (SOrderBy) {
		$(`.fields-order_by-${SOrderBy}`).prop('checked', true);
	}

	const LoadFilters = () => {
		// const vs = $('.chapter-select').val()
		const ys = $('.year-select').val()
		const cs = $('.countries-select').val()
		const gs = $('.genres-select').val()
		const ges = $('.genres-exclude-select').val()

		const filters = {
			order_by: $('.fields-order_by-input:checked').data('value'),
			// vs: vs,
			ys: ys == -1 ? -1 : ys.join(","),
			cs: cs == -1 ? -1 : cs.join(","),
			gs: gs == -1 ? -1 : gs.join(","),
			ges: ges == -1 ? -1 : ges.join(","),
		};

		$('.list').empty();
		window.loadNextPage(filters);
	}

	$('#loadFilters').on('click', function () {
		LoadFilters()
	});
	$('.field-order_by').on('change', function () {
		LoadFilters()
	});
});