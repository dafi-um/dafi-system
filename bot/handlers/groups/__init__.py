from telegram.ext import (
    CommandHandler,
    Dispatcher,
)


def load_all(dispatcher: Dispatcher) -> None:
    from .link import (
        cmd_linkgroup,
        cmd_unlinkgroup,
    )
    from .list import cmd_listgroups

    dispatcher.add_handler(CommandHandler('grupos', cmd_listgroups))

    dispatcher.add_handler(CommandHandler('vinculargrupo', cmd_linkgroup))
    dispatcher.add_handler(CommandHandler('desvinculargrupo', cmd_unlinkgroup))
