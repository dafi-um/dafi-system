from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model

from main.utils import get_url

from .handlers import add_handler, add_query_handler

User = get_user_model()

@add_handler('vincular')
def users_link(update, context):
    if update.message.chat.type != 'private':
        return 'Este comando solamente puede utilizarse en chats privados'

    telegram_user = update.message.from_user
    user = User.objects.filter(telegram_user=telegram_user.username).first()

    if user and not user.telegram_id:
        msg = (
            'He encontrado una cuenta con el email {}, '
            '¿quieres vincular esta cuenta con tu usuario de Telegram?'
        ).format(user.email)

        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('Vincular cuenta', callback_data='users:link'),
            InlineKeyboardButton('Cancelar', callback_data='main:abort')
        ]])
    elif not user:
        msg = 'No he encontrado ninguna cuenta para vincular, ' \
              'recuerda introducir tu usuario de telegram en el ' \
              'apartado Mi Perfil de la web.'

        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('Mi Perfil', url=get_url('profile')),
        ]])
    else:
        msg = 'Esta cuenta ya está vinculada a {} usuario.'.format(
            'tu' if user.telegram_id == telegram_user.id else 'otro'
        )

        reply_markup = None

    return msg, reply_markup

@add_handler('desvincular')
def users_unlink(update, context):
    if update.message.chat.type != 'private':
        return 'Este comando solamente puede utilizarse en chats privados'

    user = User.objects.filter(telegram_id=update.message.from_user.id).first()

    if not user:
        return 'Este usuario no está vinculado a ninguna cuenta.'

    msg = (
        'Vas a desvincular tu cuenta. Dejarás de recibir '
        'información importante en este chat y podrás vincular '
        'este usuario a otra cuenta. ¿Estás seguro de que deseas continuar?'
    )

    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton('Sí, desvincular cuenta', callback_data='users:unlink'),
        InlineKeyboardButton('No, cancelar', callback_data='main:abort')
    ]])

    return msg, reply_markup

@add_query_handler('users')
def users_callback_query(update, context):
    query = update.callback_query
    action = query.data.replace('users:', '')

    if action == 'link':
        user = User.objects.filter(telegram_user=query.from_user.username).first()

        if not user:
            return 'Parece que ha ocurrido un error...'

        user.telegram_id = query.from_user.id
        user.save()

        return (
            '¡He vinculado tu cuenta correctamente! '
            'Ahora te informaré de las cosas importantes por aquí.'
        )
    elif action == 'unlink':
        user = User.objects.filter(telegram_id=query.from_user.id).first()

        if not user:
            return 'Este usuario no está vinculado a ninguna cuenta.'

        user.telegram_id = None
        user.save()

        return 'He desvinculado tu cuenta correctamente.'

    return 'No hay ninguna acción disponible'
