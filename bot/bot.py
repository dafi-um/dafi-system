import logging

from os import environ, getenv
from importlib import import_module

from django import setup as django_setup

from telegram.ext import Updater, CommandHandler

def main():
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
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

    print('Starting polling...')
    updater.start_polling()

    print('Bot started!')

if __name__ == '__main__':
    main()
