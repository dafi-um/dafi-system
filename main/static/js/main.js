/*
	Introspect by TEMPLATED
	templated.co @templatedco
	Released for free under the Creative Commons Attribution 3.0 license (templated.co/license)
*/

(function($) {

	skel.breakpoints({
		xlarge:	'(max-width: 1680px)',
		large:	'(max-width: 1280px)',
		medium:	'(max-width: 980px)',
		small:	'(max-width: 736px)',
		xsmall:	'(max-width: 480px)'
	});

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) || this.crossDomain)
                return;

            xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
        }
    });

	$(function() {

		var	$window = $(window),
			$body = $('body');

		// Disable animations/transitions until the page has loaded.
			$body.addClass('is-loading');

			$window.on('load', function() {
				window.setTimeout(function() {
					$body.removeClass('is-loading');
				}, 100);
			});

		// Navigation Panel.
			$('#navPanel').panel({
				delay: 500,
				hideOnClick: true,
				hideOnSwipe: true,
				resetScroll: true,
				resetForms: true,
				side: 'left'
			});

		// Form toggles.
			$('[data-toggle]').on('click', function() {
				$(this).slideUp(200);
				$($(this).data('toggle')).slideDown(200);
			});

			$('[data-toggle-btn]').on('click', function() {
				const target = $(this).data('toggle-btn');

				$('[data-toggle="' + target + '"]').slideDown(200);
				$(target).slideUp(200);
			});

		// Comment vote.
			$('[data-action-vote]').on('click', function() {
				const $this = $(this);
				const $parent = $this.parent();

				let action = $this.data('action-vote');
				const current = $parent.data('voted');
				let className = $parent.data('class-name');

				if (!className) {
					className = 'voted';
				}

				if (action == current) {
					action = 0;
				}

				$.ajax({
					url: $parent.data('url'),
					method: 'POST',
					data: { action },
				}).done(function(res) {
					$parent.data('voted', action);
					$parent.find('.reputation').text(res.reputation);

					$parent
						.find('[data-action-vote]:not([data-action-vote="' + action + '"])')
						.removeClass(className);

					if (action != 0) {
						$parent
							.find('[data-action-vote="' + action + '"]')
							.addClass(className);
					}
				}).fail(function(res) {
					if (res.status == 403) {
						document.location.href = LOGIN_URL;
						return;
					}

					window.alert('No se pudo completar la acción.');
				});
			});

	});

})(jQuery);
