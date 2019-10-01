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

    while True:
        cmd = input('bot> ')

        if cmd == 'stop' or cmd == 'exit':
            break
        elif cmd == 'data':
            print('Persistent data:')

            for k, v in persistence.get_all():
                print('  {}: {}'.format(k, v))
        elif cmd == 'save' or cmd == 'sync':
            print('Saving persistent data...')
            persistence.sync()
            print('Done!')
        elif cmd == 'flush':
            persistence.flush()
            print('Persistent data flushed!!')
        elif cmd == 'help':
            print(
                'DAFIBot commands help:\n'
                '  data - displays persistent data in memory\n'
                '  exit - stops the bot gracefully\n'
                '  flush - flushes the persistent data\n'
                '  save - saves the persistent data to disk\n'
                '  help - displays this help'
            )
        else:
            print('Unknown command!')

    print('Stopping polling...')
    updater.stop()

    print('Saving persistent data...')
    persistence.close()

    print('Bye!')

if __name__ == '__main__':
    main()
