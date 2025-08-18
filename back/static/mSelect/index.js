$(document).ready(function () {
	class mSelect {
		constructor(element, placeholder) {
			this._element = $(element);;
			this._element.addClass('mSelect')

			this._placeholder = placeholder;

			this._options = [];
			this._options_objs = this._element.children();

			this._loadOptions();
			this._element.html('');

			this._selected = [];

			this._selectBtn = this._createSelectBtn();
			this._selectedCont = this._selectBtn.find(".mSelect-selected")
			this._optionsCont = this._createOptions();
			this._checkboxes = this._element.find('.mSelect-checkbox')

			this._selectBtn.on('click', () => {
				this._optionsCont.toggleClass('active')
			})
			$(document).on('click', (e) => {
				if (this._optionsCont.hasClass('active') && !$(e.target).closest(this._element).length) {
					this._optionsCont.removeClass('active');
				}
			});

			this._checkboxes.on('click', (e) => {
				this._chaneSelected()
			})
			this._chaneSelected()
		}

		_loadOptions() {
			const list = this._options;
			this._options_objs.each(function (i, element) {
				list.push({
					'checked': $(element).attr('data-checked') !== undefined,
					'val': $(element).data('value'),
					'cont': $(element).text(),
				})
				$(element).remove()
			});
		}

		_createSelectBtn() {
			const arrow = `<svg width="513" height="513" viewBox="0 0 513 513" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M448.5 152.5L256.5 360.5L64.5 152.5" stroke="currentColor" stroke-width="50" stroke-linecap="round"/></svg>`

			const selectedCont = $('<div>', {
				class: 'mSelect-selected'
			}).text(this._placeholder)

			const selectBtn = $('<div>', {
				class: 'mSelect-block'
			}).append(selectedCont, arrow)

			this._element.append(selectBtn)

			return selectBtn
		}

		_createOptions() {
			const optionsCont = $('<div>', {
				class: 'mSelect-options'
			})

			this._options.forEach(option => {
				const checkbox = $('<input>', {
					class: 'mSelect-checkbox',
					type: 'checkbox',
					'data-value': option['val'],
				}).prop('checked', option['checked'])

				const opt = $('<label>', {
					class: 'mSelect-option',
				}).append(checkbox, option['cont'])

				optionsCont.append(opt)
			});

			this._element.append(optionsCont)

			return optionsCont
		}

		_chaneSelected() {
			this._selected.length = 0;

			this._selected = this._checkboxes
				.filter(':checked')
				.map((i, el) => $(el).data('value'))
				.get();

			const selectedText = this._checkboxes
				.filter(':checked')
				.map((i, el) => $(el).parent().text().trim())
				.get();

			this._selectedCont.text(selectedText.length > 0 ? selectedText.join(', ') : this._placeholder)
		}

		val(value) {
			if (typeof value === 'undefined') {
				return this._selected.length === 0 ? -1 : this._selected;
			} else {
				// this._options = Array.isArray(value) ? value : [value];
				return false
			}
		}
	}
	
	$.fn.mSelect = function (placeholder) {
		return this.each(function () {
			const instance = new mSelect(this, placeholder);
			$(this).data('mSelect', instance);
		});
	};


	const originalVal = $.fn.val;

	$.fn.val = function(value) {
		if (this.data('mSelect')) {
			const instance = this.data('mSelect');
			return instance.val(value);
		} else {
			return originalVal.apply(this, arguments);
		}
	};
});