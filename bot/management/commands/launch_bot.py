import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from telegram.ext import (
    PicklePersistence,
    Updater,
)

from ...cli import BotCLI


class Command(BaseCommand):

    help = 'Launches the Telegram bot.'

    def handle(self, *args, **options):
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        logging.getLogger('apscheduler').setLevel(logging.WARNING)

        logger = logging.getLogger(__name__)
        logger.info('Launching bot...')

        persistence = PicklePersistence('bot_persistence')

        updater = Updater(
            token=settings.BOT_TOKEN,
            use_context=True,
            persistence=persistence,
        )

        logger.info('Registering handlers...')
        from ...handlers import load_all

        load_all(updater.dispatcher, updater.job_queue)

        logger.info('Starting polling...')
        updater.start_polling()

        BotCLI(persistence, updater.job_queue).cmdloop()

        logger.info('Stopping updater...')
        updater.stop()

        logger.info('Bye!')
