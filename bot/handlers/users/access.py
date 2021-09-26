from enum import Enum

from django.contrib.auth.models import Group

from telegram import Update
from telegram.ext import CallbackContext

from users.models import User

from ...decorators import auth_required
from ...utils import (
    create_users_list,
    user_display_link,
)


class AccessActions(Enum):

    VIEW = 'ver'
    ADD = 'dar'
    REMOVE = 'quitar'


USAGE_MSG = (
    'Uso:\n'
    '\t`/acceso ver <nombre-grupo>`\n'
    '\t`/acceso dar <nombre-grupo> <nombre-usuario>`\n'
    '\t`/acceso quitar <nombre-grupo> <nombre-usuario>`'
)


@auth_required('bot.can_manage_permissions')
def cmd_access(update: Update, context: CallbackContext, *args) -> None:
    assert update.effective_message is not None
    assert context.args is not None

    try:
        action = AccessActions(context.args[0])
        assert (
            (action == AccessActions.VIEW and len(context.args) == 2)
            or len(context.args) == 3
        )
    except (IndexError, ValueError):
        update.effective_message.reply_markdown(USAGE_MSG)
        return

    try:
        group = Group.objects.filter(name=context.args[1]).get()
    except Group.DoesNotExist:
        update.effective_message.reply_text(
            'No he encontrado el grupo especificado 😓'
        )
        return

    if action == AccessActions.VIEW:
        users = User.objects.filter(groups=group)

        msg = f'*Usuarios en el grupo {group.name}*:\n\n'

        update.effective_message.reply_markdown(
            msg + create_users_list(users)
        )
        return

    try:
        user = User.objects.filter(telegram_user=context.args[2]).get()
    except User.DoesNotExist:
        update.effective_message.reply_text(
            'No he encontrado el usuario especificado 😓'
        )
        return

    if action == AccessActions.ADD:
        user.groups.add(group)

        update.effective_message.reply_markdown(
            f'He agregado a {user_display_link(user)} al grupo {group.name} ✅'
        )
    elif action == AccessActions.REMOVE:
        user.groups.remove(group)

        update.effective_message.reply_markdown(
            f'He eliminado a {user_display_link(user)} del grupo {group.name} ✅'
        )
