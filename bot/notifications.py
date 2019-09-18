import os

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from main.utils import get_domain

_bot = None

if 'BOT_TOKEN' in os.environ:
    _bot = Bot(os.environ['BOT_TOKEN'])

def telegram_notify(user, message, url=None, url_button=None):
    if not _bot or not user.telegram_id:
        return False

    reply_markup = None

    if url and url_button:
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(url_button, url=get_domain() + str(url)),
        ]])

    _bot.send_message(user.telegram_id, message, reply_markup=reply_markup)
