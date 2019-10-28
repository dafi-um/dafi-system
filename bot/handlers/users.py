from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from main.utils import get_url

from .handlers import add_handler, CommandHandler, QueryHandler

User = get_user_model()


@add_handler('veracceso')
class ViewGroupsPermissions(CommandHandler):
    '''Prints the users in the given group'''

    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_permissions')

    def handle(self, update, context):
        try:
            group_name = context.args[0]
        except IndexError:
            return 'Uso: /veracceso <nombre_grupo>'

        group = Group.objects.filter(name=group_name).first()

        if not group:
            return 'No he encontrado el grupo especificado 😓'

        msg = '*Usuarios en el grupo {}*:\n'.format(group.name)

        for user in group.user_set.all():
            msg += '\n[{}](tg://user?id={})'.format(
                user.get_full_name(), user.telegram_id
            )

        return msg


class UserPermissionsMixin(CommandHandler):
    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_permissions')

    def handle(self, update, context):
        try:
            user_name, group_name = context.args
        except IndexError:
            return self.usage_msg

        username = context.args[0].strip().replace('@', '')
        user = User.objects.filter(telegram_user__iexact=username).first()

        if not user:
            return 'No he encontrado al usuario especificado 😓'
        elif not user.telegram_id:
            return 'El usuario no ha vinculado su cuenta 😓'

        group = Group.objects.filter(name=group_name).first()

        if not group:
            return 'No he encontrado el grupo especificado 😓'

        return self.do_action(user, group)


@add_handler('daracceso')
class AddUserPermissions(UserPermissionsMixin):
    '''Adds the given user to the given group'''

    usage_msg = 'Uso: /daracceso <nombre_usuario> <nombre_grupo>'

    def do_action(self, user, group):
        group.user_set.add(user)

        return 'He agregado a {} al grupo {} ✅'.format(
            user.get_full_name(), group.name
        )


@add_handler('quitaracceso')
class RemoveUserPermissions(UserPermissionsMixin):
    '''Removes the given user from the given group'''

    usage_msg = 'Uso: /daracceso <nombre_usuario> <nombre_grupo>'

    def do_action(self, user, group):
        group.user_set.remove(user)

        return 'He eliminado a {} del grupo {} ✅'.format(
            user.get_full_name(), group.name
        )


@add_handler('vincular')
class UsersLink(CommandHandler):
    '''Links a telegram user to a django user'''

    chat_type = 'private'

    def handle(self, update, context):
        telegram_user = update.message.from_user
        user = User.objects.filter(telegram_user__iexact=telegram_user.username).first()

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
            user = User.objects.filter(telegram_user__iexact=query.from_user.username).first()

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
