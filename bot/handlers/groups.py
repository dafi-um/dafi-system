from telegram.error import BadRequest

from django.contrib.auth import get_user_model
from django.db.models import Q

from heart.models import Group

from .handlers import add_handler

User = get_user_model()

@add_handler('vinculargrupo')
def groups_link(update, context):
    message = update.message

    if message.chat.type != 'group':
        return 'Este comando solamente puede utilizarse en grupos'

    try:
        group_year, group_num = [int(x) for x in context.args[0].split('.')]
    except (ValueError, IndexError):
        return (
            '**Uso**: _/vinculargrupo <curso>.<grupo>_\n\n'
            '**Ej**: para el grupo 1 de tercero usa `/vinculargrupo 3.1`'
        )

    bot_id = context.bot.get_me().id

    if message.chat.get_member(bot_id).status != 'administrator':
        return 'El bot debe ser administrador para vincular el grupo'

    group_id = str(message.chat.id)

    group = Group.objects.filter(telegram_group=group_id).first()

    if group:
        if group.year == group_year and group.number == group_num:
            return 'Este chat de Telegram ya se ha vinculado a este grupo'
        else:
            return 'Este chat de Telegram ya está vinculado al grupo {}.{}'.format(group.year, group.number)

    user = User.objects.filter(telegram_id=message.from_user.id).first()

    if not user:
        return (
            'Debes vincular tu cuenta de usuario primero: '
            'ejecuta /vincular en un chat privado conmigo'
        )

    query = Q(year=group_year, number=group_num)

    if not user.has_perm('can_link_group'):
        query &= Q(delegate=user) | Q(subdelegate=user)

    group = Group.objects.filter(query).first()

    if not group:
        return 'No se ha encontrado el grupo indicado o el usuario no es un delegado'

    group.telegram_group = group_id

    try:
        group.telegram_group_link = context.bot.export_chat_invite_link(group_id)
    except BadRequest:
        return 'Ha ocurrido un error inesperado durante la vinculación'

    group.save()

    return '¡Grupo vinculado correctamente!'
