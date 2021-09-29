from datetime import time

import pytz
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
    JobQueue,
)


def load_all(dispatcher: Dispatcher, job_queue: JobQueue) -> None:
    from .basic import (
        callback_generic,
        cmd_getid,
        cmd_start,
    )
    from .broadcast import (
        callback_broadcast,
        cmd_broadcast,
    )
    from .conversation import cmd_mention
    from .elections import load_all as load_elections_handlers
    from .groups import load_all as load_groups_handlers
    from .rooms import (
        callback_dafi,
        cmd_dafi,
        job_dafi,
    )
    from .users import load_all as load_users_handlers

    tzinfo = pytz.timezone('Europe/Madrid')

    # Basic
    dispatcher.add_handler(CallbackQueryHandler(callback_generic, pattern='main'))
    dispatcher.add_handler(CommandHandler('getid', cmd_getid))
    dispatcher.add_handler(CommandHandler('start', cmd_start))

    # Broadcast
    dispatcher.add_handler(CallbackQueryHandler(callback_broadcast, pattern='broadcast'))
    dispatcher.add_handler(CommandHandler('broadcast', cmd_broadcast))

    # Conversation
    dispatcher.add_handler(CommandHandler('mencionar', cmd_mention))

    # Rooms
    dispatcher.add_handler(CallbackQueryHandler(callback_dafi, pattern='dafi'))
    dispatcher.add_handler(CommandHandler('dafi', cmd_dafi))
    job_queue.run_daily(job_dafi, time(hour=21, minute=10, tzinfo=tzinfo))

    load_elections_handlers(dispatcher)
    load_groups_handlers(dispatcher)
    load_users_handlers(dispatcher)
