$(document).ready(function () {
	const SOrderBy = sessionStorage.getItem('order_by');

	let isLoading = false;
	let hasNext = true;
	var pageNumber = 0;
	let currentFilters = {};

	window.loadNextPage = (newFilters=null) => {
		if (!hasNext) return;

		if (newFilters !== null) {
			currentFilters = newFilters;
			pageNumber = 0;
			hasNext = true;
		}

		isLoading = true;
		$('#loader').show();
		pageNumber++

		const ajaxParams = new URLSearchParams();
		ajaxParams.set('p', pageNumber);

		for (const [key, value] of Object.entries(currentFilters)) {
			ajaxParams.set(key, value);
		}


		if (!ajaxParams.get('order_by') && SOrderBy) {
			ajaxParams.set('order_by', SOrderBy)
		}
		sessionStorage.setItem('order_by', ajaxParams.get('order_by'));

		$.ajax({
			url: `?${ajaxParams.toString()}`,
			type: 'GET',
			success: function(data) {
				if (pageNumber === 1) {
					$('.list').empty();
				}
				$('.list').append(data.list);

				hasNext = data.has_next;
				isLoading = false;
				$('#loader').hide();
			},
			error: function() {
				isLoading = false;
				$('#loader').hide();
			}
		});
	}
	window.loadNextPage()


	$('.content').on("scroll", function () {
		var h = 0
		$(this).children().each(function (index, element) {
			h += $(this).height()
		});
		if (!isLoading && ($(this).scrollTop() + $(this).height()) >= h - 50) { // $(this).scrollTop() + $(this).height() >= $(document).height() - 500
			isLoading = true;

			loadNextPage()
		}
	});
});

// 	// if (!params.has('p') || params.get('p') != pageNumber) {
// 	// 	params.set('p', pageNumber);
// 	// 	const newUrl = `${window.location.pathname}?${params.toString()}`;
// 	// 	history.replaceState(null, '', newUrl);
// 	// }