from telegram.ext import CommandHandler

from django.core.exceptions import ValidationError
from django.db.models import Q

from heart.models import Group

def groups_link(update, context):
    message = update.message

    if message.chat.type != 'group':
        message.reply_text('Este comando solamente puede utilizarse en grupos')
        return

    bot_id = context.bot.get_me().id

    if message.chat.get_member(bot_id).status != 'administrator':
        message.reply_text('El bot debe ser administrador para vincular el grupo')
        return

    user_id = message.from_user.id
    group_id = message.chat.id

    group = Group.objects.filter(
        Q(telegram_group=group_id)
        | Q(delegate__telegram_id=user_id)
        | Q(subdelegate__telegram_id=user_id)
    ).first()

    if not group:
        msg = 'Este comando debe ser ejecutado por un delegado'
    elif group.telegram_group == group_id:
        msg = 'Este grupo ya ha sido vinculado'
    elif group.telegram_group:
        msg = 'No puedes vincular este grupo'
    else:
        group.telegram_group = group_id
        group.telegram_group_link = context.bot.export_chat_invite_link(group_id)

        try:
            group.save()
            msg = '¡Grupo vinculado correctamente!'
        except ValidationError:
            msg = 'Ha ocurrido un error durante la vinculación'

    message.reply_text(msg)

def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('vinculargrupo', groups_link))
