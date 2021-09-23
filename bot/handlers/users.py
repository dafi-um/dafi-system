from typing import Callable, Dict, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from main.utils import get_url
from telegram import ParseMode
from telegram.ext import CallbackContext, Updater

from ..utils import create_reply_markup, create_users_list
from .handlers import BasicBotHandler, add_handlers

User = get_user_model()


@add_handlers
class Permissions(BasicBotHandler):
    ''' Manage the groups and users'''
    cmd: str = "acceso"

    user_required = True

    usage_msg: str = (
        "Uso:\n"
        "\t`/acceso ver <nombre-grupo>`\n"
        "\t`/acceso dar <nombre-usuario> <nombre-grupo>`\n"
        "\t`/acceso quitar <nombre-usuario> <nombre-grupo>`"
    )

    def view_acces(self, update: Updater, context: CallbackContext) -> str:
        try:
            group_name: str = context.args[1]
        except IndexError:
            return 'Uso: `/acceso ver <nombre-grupo>`'

        group: Optional[Group] = Group.objects.filter(name=group_name).first()

        if not group:
            return 'No he encontrado el grupo especificado 😓'

        msg: str = '*Usuarios en el grupo {}*:\n'.format(group.name)

        return msg + create_users_list(group.user_set.all())

    def add_access(self, update: Updater, context: CallbackContext) -> str:
        try:
            user_name: str = context.args[1]
            group_name: str = context.args[2]
        except IndexError:
            return 'Uso: `/acceso dar <nombre-usuario> <nombre-grupo>`'

        group: Group = Group.objects.filter(name=group_name).first()
        if not group:
            return 'No he encontrado el grupo especificado 😓'

        user: User = User.objects.filter(telegram_user=user_name).first()
        if not user:
            return 'No he encontrado el usuario especificado 😓'

        group.user_set.add(user)
        return 'He agregado a {} al grupo {} ✅'.format(
            user.get_full_name(), group.name
        )

    def remove_access(self, update: Updater, context: CallbackContext) -> str:
        try:
            user_name: str = context.args[1]
            group_name: str = context.args[2]
        except IndexError:
            return 'Uso: `/acceso quitar <nombre-usuario> <nombre-grupo>`'

        group: Group = Group.objects.filter(name=group_name).first()
        user: User = User.objects.filter(telegram_user=user_name).first()

        if not group:
            return 'No he encontrado el grupo especificado 😓'
        if not user:
            return 'No he encontrado el usuario especificado 😓'

        group.user_set.remove(user)
        return 'He eliminado a {} del grupo {} ✅'.format(
            user.get_full_name(), group.name
        )

    _dispatch_table: Dict[str, Callable[["Permissions", Updater, CallbackContext], str]] = {
        "ver": view_acces,
        "dar": add_access,
        "quitar": remove_access,
    }

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_permissions')

    def command(self, update: Updater, context: CallbackContext) -> str:
        try:
            option: str = context.args[0]
        except IndexError:
            return self.usage_msg

        method: Callable[[Permissions, Updater, CallbackContext], str] = self._dispatch_table.get(option)
        if method is not None:
            return method(self, update, context)
        else:
            return self.usage_msg


@add_handlers
class BroadcastToGroup(BasicBotHandler):
    '''Broadcasts a message to the users in the given group'''

    cmd = 'broadcastgrupo'

    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_permissions')

    def command(self, update, context):
        try:
            group_name = context.args[0]
            text = ' '.join(context.args[1:])
        except IndexError:
            return 'Uso: `/{} <nombre-grupo> <mensaje>`'.format(self.cmd)

        group = Group.objects.filter(name=group_name).first()

        if not group:
            return 'No he encontrado el grupo especificado 😓'

        sent_text = 'Mensaje para miembros de *{}*:\n\n_{}_'.format(
            group.name, text
        )

        sent = 0
        fails = 0

        for user in group.user_set.all():
            try:
                context.bot.send_message(
                    user.telegram_id, sent_text, ParseMode.MARKDOWN
                )

                sent += 1
            except:
                # So many errors can occur here but it's a simple
                # notification, so we'll just ignore a failed one
                fails += 1

        msg = 'Mensaje enviado a {} usuarios:\n\n_{}_'.format(sent, text)

        if fails:
            msg += '\n\nNo se pudo enviar a {} usuarios.'.format(fails)

        return msg


class UserPermissionsMixin(BasicBotHandler):
    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_permissions')

    def do_action(self, user, group):
        raise NotImplementedError("Must create a `do_action' method in the class")

    def command(self, update, context):
        try:
            user_name, group_name = context.args
        except ValueError:
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


@add_handlers
class UsersLink(BasicBotHandler):
    '''Links a telegram user to a django user'''

    cmd = 'vincular'

    chat_type = 'private'

    def command(self, update, context):
        telegram_user = update.message.from_user
        user = User.objects.filter(telegram_user__iexact=telegram_user.username).first()

        if user and not user.telegram_id:
            msg = (
                'He encontrado una cuenta con el email {}, '
                '¿quieres vincular esta cuenta con tu usuario de Telegram?'
            ).format(user.email)

            reply_markup = create_reply_markup([
                ('Vincular cuenta', 'users:link'),
                ('Cancelar', 'main:abort'),
            ])
        elif not user:
            msg = (
                'No he encontrado ninguna cuenta para vincular, '
                'recuerda introducir tu usuario de telegram en el '
                'apartado Mi Perfil de la web.'
            )

            reply_markup = create_reply_markup([
                ('Mi Perfil', None, get_url('profile')),
            ])
        else:
            if user.telegram_id == telegram_user.id:
                msg_end = 'tu usuario ✅'
            else:
                msg_end = 'otro usuario ⚠️'

            return 'Esta cuenta ya está vinculada a ' + msg_end

        return msg, reply_markup


@add_handlers
class UsersUnlink(BasicBotHandler):
    '''Unlinks a telegram user from a django user'''

    cmd = 'desvincular'

    user_required = True
    user_required_msg = 'Este usuario no está vinculado a ninguna cuenta.'

    chat_type = 'private'

    def command(self, update, context):
        msg = (
            '⚠️ Vas a desvincular tu cuenta ⚠️\n'
            'No podrás realizar acciones importantes salvo que vincules '
            'tu cuenta de nuevo. ¿Estás seguro de que deseas continuar?'
        )

        reply_markup = create_reply_markup([
            ('Sí, desvincular cuenta', 'users:unlink'),
            ('No, cancelar', 'main:abort'),
        ])

        return msg, reply_markup


@add_handlers
class UsersCallbackHandler(BasicBotHandler):
    '''Link and unlink command buttons callbacks'''

    query_prefix = 'users'

    def callback(self, update, context, action, *args):
        if action == 'link':
            telegram_user = update.effective_user

            user = (
                User
                .objects
                .filter(telegram_user__iexact=telegram_user.username)
                .first()
            )

            if not user:
                return 'Parece que ha ocurrido un error...'

            user.telegram_id = telegram_user.id
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
