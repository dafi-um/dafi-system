import logging
import schedule

from importlib import import_module
from os import environ, getenv

from django import setup as django_setup

from telegram.ext import Updater, CommandHandler

from .jobs import SchedulerThread, load_jobs

from .cli import BotCLI

def main():
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.WARNING
    )

    environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

    print('Setting up Django...')

    django_setup()

    token = getenv('BOT_TOKEN')

    if not token:
        raise Exception('Bot token not found')

    updater = Updater(token=token, use_context=True)

    print('Loading handlers...')

    from . import handlers, persistence

    for handler in handlers.get_handlers():
        updater.dispatcher.add_handler(handler)

    print('Loading persistent data...')
    persistence.load()

    print('Loading scheduled jobs...')
    load_jobs(updater.bot)

    print('Starting scheduler thread...')
    thread = SchedulerThread()
    thread.start()

    print('Starting polling...')
    updater.start_polling()

    BotCLI().cmdloop()

    print('Stopping scheduler thread...')
    thread.stopper.set()
    thread.join()

    print('Stopping polling...')
    updater.stop()

    print('Saving persistent data...')
    persistence.close()

    print('Bye!')

if __name__ == '__main__':
    main()
