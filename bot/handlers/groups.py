from telegram.error import BadRequest

from django.contrib.auth import get_user_model
from django.db.models import Q

from heart.models import Group

from .handlers import add_handler, CommandHandler

User = get_user_model()


@add_handler('vinculargrupo')
class GroupsLink(CommandHandler):
    '''Links a telegram group to a students group (only staff and delegates)'''

    chat_type = 'group'

    bot_admin_required = True
    user_required = True

    def handle(self, update, context):
        message = update.message

        try:
            group_year, group_num = [int(x) for x in context.args[0].split('.')]
        except (ValueError, IndexError):
            return (
                '**Uso**: _/vinculargrupo <curso>.<grupo>_\n\n'
                '**Ej**: para el grupo 1 de tercero usa `/vinculargrupo 3.1`'
            )

        chat_id = str(update.effective_chat.id)
        group = Group.objects.filter(telegram_group=chat_id).first()

        if group:
            return (
                'Este chat de Telegram ya está vinculado al grupo {}.{}'
            ).format(group.year, group.number)

        user = self.get_user()

        query = Q(year=group_year, number=group_num)

        if not user.has_perm('heart.can_link_group'):
            query &= Q(delegate=user) | Q(subdelegate=user)

        group = Group.objects.filter(query).first()

        if not group:
            return 'No se ha encontrado el grupo indicado o el usuario no es un delegado'

        group.telegram_group = chat_id

        try:
            group.telegram_group_link = context.bot.export_chat_invite_link(chat_id)
        except BadRequest:
            return 'Ha ocurrido un error inesperado durante la vinculación'

        group.save()

        return '¡Grupo vinculado correctamente!'


@add_handler('desvinculargrupo')
class GroupsUnlink(CommandHandler):
    '''Unlinks a telegram group from a students group (only staff and delegates)'''

    chat_type = 'group'

    user_required = True

    def handle(self, update, context):
        group = Group.objects.filter(telegram_group=update.message.chat.id).first()

        if not group:
            return '⚠️ Este chat de Telegram no está vinculado a ningún grupo ⚠️'

        user = self.get_user()

        if (not user.has_perm('heart.can_link_group')
                and not user == group.delegate
                and not user == group.subdelegate):
            return 'No tienes los permisos necesarios para ejecutar este comando'

        group.telegram_group = ''
        group.telegram_group_link = ''

        group.save()

        return 'Grupo desvinculado correctamente'
