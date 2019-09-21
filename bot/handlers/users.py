from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model

from main.utils import get_url

from .handlers import add_handler, CommandHandler, QueryHandler

User = get_user_model()


@add_handler('vincular')
class UsersLink(CommandHandler):
    '''Links a telegram user to a django user'''

    chat_type = 'private'

    def handle(self, update, context):
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
            msg = (
                'No he encontrado ninguna cuenta para vincular, '
                'recuerda introducir tu usuario de telegram en el '
                'apartado Mi Perfil de la web.'
            )

            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton('Mi Perfil', url=get_url('profile')),
            ]])
        else:
            if user.telegram_id == telegram_user.id:
                msg_end = 'tu usuario ✅'
            else:
                msg_end = 'otro usuario ⚠️'

            return 'Esta cuenta ya está vinculada a ' + msg_end

        return msg, reply_markup


@add_handler('desvincular')
class UsersUnlink(CommandHandler):
    '''Unlinks a telegram user from a django user'''

    user_required = True
    user_required_msg = 'Este usuario no está vinculado a ninguna cuenta.'

    chat_type = 'private'

    def handle(self, update, context):
        msg = (
            '⚠️ Vas a desvincular tu cuenta ⚠️\n'
            'No podrás realizar acciones importantes salvo que vincules '
            'tu cuenta de nuevo. ¿Estás seguro de que deseas continuar?'
        )

        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('Sí, desvincular cuenta', callback_data='users:unlink'),
            InlineKeyboardButton('No, cancelar', callback_data='main:abort')
        ]])

        return msg, reply_markup


@add_handler('users')
class UsersCallbackHandler(QueryHandler):
    '''Link and unlink command buttons callbacks'''

    def handle(self, update, context):
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
            user = self.get_user()

            if not user:
                return 'Este usuario no está vinculado a ninguna cuenta.'

            user.telegram_id = None
            user.save()

            return 'He desvinculado tu cuenta correctamente.'
