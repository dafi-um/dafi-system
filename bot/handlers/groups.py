import telegram
from telegram.error import BadRequest
from telegram.ext import CommandHandler

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q

from heart.models import Group

User = get_user_model()

def groups_link(update, context):
    message = update.message

    if message.chat.type != 'group':
        message.reply_text('Este comando solamente puede utilizarse en grupos')
        return

    param = context.args[0]

    try:
        group_year, group_num = [int(x) for x in param.split('.')]
    except (ValueError, IndexError):
        message.reply_text(
            '**Uso**: _/vinculargrupo <curso>.<grupo>_\n\n'
            '**Ej**: para grupo 1 de tercero usa `/vinculargrupo 3.1`'
        , parse_mode=telegram.ParseMode.MARKDOWN)
        return

    bot_id = context.bot.get_me().id

    if message.chat.get_member(bot_id).status != 'administrator':
        message.reply_text('El bot debe ser administrador para vincular el grupo')
        return

    group_id = str(message.chat.id)

    group = Group.objects.filter(telegram_group=group_id).first()

    if group:
        if group.year == group_year and group.number == group_num:
            msg = 'Este chat de Telegram ya se ha vinculado a este grupo'
        else:
            msg = 'Este chat de Telegram ya está vinculado al grupo {}.{}'.format(group.year, group.number)

        message.reply_text(msg)
        return

    user = User.objects.filter(telegram_id=message.from_user.id).first()

    if not user:
        message.reply_text(
            'Debes vincular tu cuenta de usuario primero: '
            'ejecuta /vincular en un chat privado conmigo'
        )
        return

    query = Q(year=group_year, number=group_num)

    if not user.has_perm('can_link_group'):
        query &= Q(delegate=user) | Q(subdelegate=user)

    group = Group.objects.filter(query).first()

    if not group:
        msg = 'No se ha encontrado el grupo indicado o el usuario no es un delegado'
    else:
        group.telegram_group = group_id

        try:
            group.telegram_group_link = context.bot.export_chat_invite_link(group_id)
        except BadRequest:
            msg = 'Ha ocurrido un error inesperado durante la vinculación'
        else:
            group.save()
            msg = '¡Grupo vinculado correctamente!'

    message.reply_text(msg)

def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('vinculargrupo', groups_link))
