from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler

from django.contrib.auth import get_user_model

User = get_user_model()

def start(update, context):
    telegram_user = update.message.from_user
    user = User.objects.filter(telegram_user=telegram_user.username).first()

    update.message.reply_text(
        'Hola {}, soy el DAFI Bot. ¿En qué puedo ayudarte?'.format(telegram_user.first_name)
    )

    if user and not user.telegram_id:
        msg = (
            'He encontrado una cuenta de DAFI ({}) '
            'con tu usuario de Telegram, ¿quieres vincularla '
            'ahora a tu cuenta de Telegram?'
        ).format(user.email)

        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('Sí, vincular cuenta', callback_data='users:link'),
            InlineKeyboardButton('No, cancelar', callback_data='main:abort')
        ]])

        update.message.reply_text(msg, reply_markup=reply_markup)

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
