from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model

from .handlers import add_handler, add_query_handler

User = get_user_model()

@add_handler('start')
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

        return msg, reply_markup

@add_query_handler('main')
def basic_callback(update, context):
    if update.callback_query.data == 'main:abort':
        return 'Operación cancelada.'
