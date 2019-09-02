from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.ext import CallbackQueryHandler, CommandHandler

from django.contrib.auth import get_user_model

User = get_user_model()

def start(update, context):
    user = User.objects.filter(telegram_user=update.message.from_user.username).first()

    update.message.reply_text('Hola {}, soy el DAFI Bot. ¿En qué puedo ayudarte?'.format(update.message.from_user.first_name))

    if user and not user.telegram_id:
        update.message.reply_text('He encontrado una cuenta con tu usuario de Telegram, quizás deberías ejecutar /vincular para vincularla.')

def error_callback(bot, update, error):
    print(error)

def basic_callback(update, context):
    update.callback_query.answer()

    if update.callback_query.data == 'main:abort':
        msg = 'Operación cancelada.'
    else:
        msg = 'Parece que ha ocurrido un error...'

    update.callback_query.edit_message_text(msg, reply_markup=None)

def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(basic_callback, pattern='main'))
    dispatcher.add_error_handler(error_callback)
