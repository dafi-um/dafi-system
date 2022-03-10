from telegram.ext import (
    CommandHandler,
    Dispatcher,
)


def load_all(dispatcher: Dispatcher) -> None:
    from .link import (
        cmd_linkgroup,
        cmd_linkyear,
        cmd_unlinkgroup,
        cmd_unlinkyear,
    )
    from .list import cmd_listgroups

    dispatcher.add_handler(CommandHandler('grupos', cmd_listgroups))

    dispatcher.add_handler(CommandHandler('vinculargrupo', cmd_linkgroup))
    dispatcher.add_handler(CommandHandler('desvinculargrupo', cmd_unlinkgroup))

    dispatcher.add_handler(CommandHandler('vincularanyo', cmd_linkyear))
    dispatcher.add_handler(CommandHandler('desvincularanyo', cmd_unlinkyear))
