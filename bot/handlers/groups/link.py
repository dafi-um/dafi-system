from telegram import Update
from telegram.ext import CallbackContext

from bot.utils import generate_invite_link
from heart.models import Group
from users.models import User

from ...decorators import (
    auth_required,
    bot_admin_required,
    limit_chat_type,
)


@limit_chat_type('group')
@bot_admin_required()
@auth_required('heart.can_link_group')
def cmd_linkgroup(update: Update, context: CallbackContext, user: User) -> None:
    assert context.args is not None
    assert update.effective_chat is not None
    assert update.effective_message is not None

    try:
        group_id = int(context.args[0])
    except (ValueError, IndexError):
        update.effective_message.reply_markdown(
            'Uso: `/vinculargrupo <ID>`'
        )
        return

    existing = Group.objects.filter(telegram_group=update.effective_chat.id).first()

    if existing:
        update.effective_message.reply_text(
            f'Este chat de Telegram ya está vinculado al grupo {existing.display_title} ⚠️'
        )

    try:
        group = Group.objects.filter(id=group_id).get()
    except Group.DoesNotExist:
        update.effective_message.reply_text(
            'No se ha encontrado el grupo indicado o el usuario '
            'no es un delegado de ese grupo ❌'
        )
        return

    invite_link = generate_invite_link(update.effective_chat, context.bot)

    if not invite_link:
        update.effective_message.reply_text(
            'Ha ocurrido un error inesperado durante la vinculación ⚠️'
        )
        return

    group.telegram_group = update.effective_chat.id
    group.telegram_group_link = invite_link
    group.save(update_fields=('telegram_group', 'telegram_group_link'))

    update.effective_message.reply_text(
        '¡Grupo vinculado correctamente! 🎉'
    )


@limit_chat_type('group')
@auth_required('heart.can_link_group')
def cmd_unlinkgroup(update: Update, context: CallbackContext, user: User) -> None:
    assert update.effective_chat is not None
    assert update.effective_message is not None

    updated = (
        Group
        .objects
        .filter(telegram_group=update.effective_chat.id)
        .update(telegram_group=None, telegram_group_link=None)
    )

    if not updated:
        update.effective_message.reply_text(
            '⚠️ Este chat de Telegram no está vinculado a ningún grupo ⚠️'
        )
        return

    update.effective_message.reply_text(
        '¡Grupo desvinculado correctamente! ✅'
    )
