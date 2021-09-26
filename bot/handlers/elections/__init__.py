from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
)


def load_all(dispatcher: Dispatcher) -> None:
    from .delegates import (
        cmd_im_delegate,
        cmd_im_subdelegate,
    )
    from .management import (
        callback_delegate_request,
        callback_toggle_elections,
        cmd_toggle_elections,
    )

    dispatcher.add_handler(CommandHandler('soydelegado', cmd_im_delegate))
    dispatcher.add_handler(CommandHandler('soysubdelegado', cmd_im_subdelegate))

    dispatcher.add_handler(CommandHandler('elecciones', cmd_toggle_elections))

    dispatcher.add_handler(CallbackQueryHandler(callback_delegate_request, pattern='elections_request'))
    dispatcher.add_handler(CallbackQueryHandler(callback_toggle_elections, pattern='elections_toggle'))
