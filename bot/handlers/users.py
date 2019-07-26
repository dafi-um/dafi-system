from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from django.contrib.auth import get_user_model

User = get_user_model()

def users_link(update, context):
    username = update.message.from_user.username
    id = update.message.from_user.id

    user = User.objects.filter(telegram_user=update.message.from_user.username).first()

    if user and not user.telegram_id:
        buttons = [[
            InlineKeyboardButton('Vincular cuenta', callback_data='users:link'),
            InlineKeyboardButton('Cancelar', callback_data='main:abort')
        ]]

        msg = 'He encontrado una cuenta con el email {}, ¿quieres vincular esta cuenta con tu usuario de Telegram?'.format(user.email)
        reply_markup = InlineKeyboardMarkup(buttons)
    elif not user:
        msg = 'No he podido continuar porque no existe ninguna cuenta con este usuario de Telegram'
        reply_markup = None
    else:
        msg = 'Esta cuenta ya está vinculada a {} usuario.'.format('tu' if user.telegram_id == id else 'otro')
        reply_markup = None

    update.message.reply_text(msg, reply_markup=reply_markup)

def users_unlink(update, context):
    user = User.objects.filter(telegram_id=update.message.from_user.id).first()

    if user:
        buttons = [[
            InlineKeyboardButton('Sí, desvincular cuenta', callback_data='users:unlink'),
            InlineKeyboardButton('No, cancelar', callback_data='main:abort')
        ]]

        msg = 'Vas a desvincular tu cuenta. Dejarás de recibir información importante en este chat y podrás vincular este usuario a otra cuenta. ¿Estás seguro de que deseas continuar?'
        reply_markup = InlineKeyboardMarkup(buttons)
    else:
        msg = 'Este usuario no está vinculado a ninguna cuenta.'
        reply_markup = None

    update.message.reply_text(msg, reply_markup=reply_markup)

def users_callback_query(update, context):
    if update.callback_query.data == 'users:link':
        user = User.objects.filter(telegram_user=update.callback_query.from_user.username).first()

        if user:
            user.telegram_id = update.callback_query.from_user.id
            user.save()

            msg = '¡He vinculado tu cuenta correctamente! Ahora te informaré de las cosas importantes también por aquí.'
        else:
            msg = 'Parece que ha ocurrido un error...'
    elif update.callback_query.data == 'users:unlink':
        user = User.objects.filter(telegram_id=update.callback_query.from_user.id).first()

        if user:
            user.telegram_id = None
            user.save()

            msg = 'He desvinculado tu cuenta correctamente.'
        else:
            msg = 'Este usuario no está vinculado a ninguna cuenta.'
    else:
        msg = 'No hay ninguna acción disponible'

    update.callback_query.answer()
    update.callback_query.edit_message_text(msg, reply_markup=None)

def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('vincular', users_link))
    dispatcher.add_handler(CommandHandler('desvincular', users_unlink))
    dispatcher.add_handler(CallbackQueryHandler(users_callback_query, pattern='users'))
