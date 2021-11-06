(function($) {

    let question = 0;

    const $questions = $('.selector-question');
    const $finish = $('#selector-finish');
    const $loading = $('#selector-loading');

    const $actionPrev = $('#selector-prev');
    const $actionNext = $('#selector-next');

    const goToQuestion = () => {
        $questions
            .hide()
            .filter('[question="' + question + '"]')
            .show();

        $actionPrev.toggle(question > 0);
        $actionNext.toggle(question < MAX_QUESTIONS);
    }

    $('#selector-start').click(function() {
        if (question == 0) {
            $(this).parent('div').hide();

            goToQuestion();
        }
    });

    $actionPrev.click(() => {
        if (question > 0) {
            question--;

            goToQuestion();
        }
    });

    $actionNext.click(() => {
        if (question < MAX_QUESTIONS) {
            question++;

            goToQuestion();
        }
    });

    $finish.click(() => {
        if (question == MAX_QUESTIONS) {
            $actionPrev.hide();
            $loading.css('display', 'inline-block');
            $finish.hide();
        }
    });

})(jQuery);
