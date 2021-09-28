from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
)


def load_all(dispatcher: Dispatcher) -> None:
    from .access import cmd_access
    from .link import (
        callback_link,
        callback_unlink,
        cmd_link,
        cmd_unlink,
    )

    dispatcher.add_handler(CommandHandler('acceso', cmd_access))

    dispatcher.add_handler(CallbackQueryHandler(callback_link, pattern='users:link'))
    dispatcher.add_handler(CallbackQueryHandler(callback_unlink, pattern='users:unlink'))
    dispatcher.add_handler(CommandHandler('vincular', cmd_link))
    dispatcher.add_handler(CommandHandler('desvincular', cmd_unlink))
