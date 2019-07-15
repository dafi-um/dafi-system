from os import environ, getenv
from importlib import import_module

from django import setup as django_setup

from telegram.ext import Updater, CommandHandler

handlers = [
    'basic',
    'blog',
]

if __name__ == '__main__':
    environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

    django_setup()

    token = getenv('BOT_TOKEN')

    if not token:
        raise Exception('Bot token not found')

    updater = Updater(token=token, use_context=True)

    # Fixes bug in python <= 3.5: parent module not initiated
    import_module('bot.handlers')

    for name in handlers:
        mod = import_module('.' + name, 'bot.handlers')

        mod.add_handlers(updater.dispatcher)

    updater.start_polling()
