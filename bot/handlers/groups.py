from telegram import ParseMode
from telegram.error import BadRequest

from django.contrib.auth import get_user_model
from django.db.models import Q

from heart.models import Group
from clubs.models import Club

from .handlers import add_handlers, BasicBotHandler

User = get_user_model()


@add_handlers
class GroupsList(BasicBotHandler):
    '''Returns a list of all the groups'''

    cmd = 'grupos'

    def command(self, update, context):
        groups = (
            Group
            .objects
            .filter(~Q(telegram_group_link=''))
            .order_by('course', 'year', 'number')
        )

        msg = '*~~Grupos de Telegram~~*\n'

        y = None

        for group in groups:
            if group.year != y:
                y = group.year
                msg += '\n'

            if group.course == group.GII:
                name = '{} {}º {}'.format(group.course, group.year, group.name)
            else:
                name = group.name

            msg += '[{}]({})\n'.format(name, group.telegram_group_link)

        return msg


@add_handlers
class GroupsLink(BasicBotHandler):
    '''Links a telegram group to a students group (only staff and delegates)'''

    cmd = 'vinculargrupo'

    chat_type = 'group'

    bot_admin_required = True
    user_required = True

    def command(self, update, context):
        try:
            group_year, group_num = [int(x) for x in context.args[0].split('.')]
        except (ValueError, IndexError):
            return (
                '**Uso**: _/vinculargrupo <curso>.<grupo>_\n\n'
                '**Ej**: para el grupo 1 de tercero usa `/vinculargrupo 3.1`'
            )

        group = Group.objects.filter(telegram_group=update.effective_chat.id).first()

        if group:
            return (
                'Este chat de Telegram ya está vinculado al grupo {}.{} ⚠️'
            ).format(group.year, group.number)

        user = self.get_user()

        query = Q(year=group_year, number=group_num)

        if not user.has_perm('heart.can_link_group'):
            query &= Q(delegate=user) | Q(subdelegate=user)

        group = Group.objects.filter(query).first()

        if not group:
            return 'No se ha encontrado el grupo indicado o el usuario no es un delegado'
        elif group.telegram_group:
            return 'El grupo {}.{} ya está vinculado a otro chat ⚠️'.format(group_year, group_num)

        chat_id, invite_link = self.get_invite_link()

        if not chat_id or not invite_link:
            return 'Ha ocurrido un error inesperado durante la vinculación'

        group.telegram_group = chat_id
        group.telegram_group_link = invite_link
        group.save()

        return '¡Grupo vinculado correctamente!'


@add_handlers
class GroupsUnlink(BasicBotHandler):
    '''Unlinks a telegram group from a students group (only staff and delegates)'''

    cmd = 'desvinculargrupo'

    chat_type = 'group'

    user_required = True

    def command(self, update, context):
        group = (
            Group
            .objects
            .filter(telegram_group=update.message.chat.id)
            .prefetch_related('delegate')
            .prefetch_related('subdelegate')
            .first()
        )

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


@add_handlers
class GroupsLink(BasicBotHandler):
    '''Links a telegram group to a club (only staff and managers)'''

    cmd = 'vincularclub'

    chat_type = 'group'

    bot_admin_required = True
    user_required = True

    def command(self, update, context):
        if not context.args or not context.args[0]:
            return '**Uso**: _/vincularclub <ID-del-club>_'

        slug = context.args[0]
        chat_id = str(update.effective_chat.id)
        query = Q(telegram_group=chat_id) | Q(slug=slug)

        club = (
            Club
            .objects
            .filter(query)
            .prefetch_related('managers')
            .first()
        )

        if not club:
            return 'No se ha encontrado el club _{}_'.format(slug)
        elif club.telegram_group == chat_id:
            return 'Este chat ya está vinculado a _{}_ ⚠️'.format(club.name)
        elif club.telegram_group:
            return 'El club _{}_ ya está vinculado a otro chat ⚠️'.format(club.name)

        user = self.get_user()

        if not user.is_superuser and user not in club.managers.all():
            return 'No tienes permisos para realizar esta acción ⚠️'

        chat_id, invite_link = self.get_invite_link()

        if not chat_id or not invite_link:
            return 'Ha ocurrido un error inesperado durante la vinculación'

        club.telegram_group = chat_id
        club.telegram_group_link = invite_link
        club.save()

        return '¡Club vinculado correctamente!'


@add_handlers
class GroupsUnlink(BasicBotHandler):
    '''Unlinks a telegram group from a club (only staff and managers)'''

    cmd = 'desvincularclub'

    chat_type = 'group'

    user_required = True

    def command(self, update, context):
        club = (
            Club
            .objects
            .filter(telegram_group=update.message.chat.id)
            .prefetch_related('managers')
            .first()
        )

        if not club:
            return '⚠️ Este chat de Telegram no está vinculado a ningún club ⚠️'

        user = self.get_user()

        if not user.is_superuser and user not in club.managers.all():
            return 'No tienes los permisos necesarios para ejecutar este comando ⚠️'

        club.telegram_group = ''
        club.telegram_group_link = ''

        club.save()

        return '¡Club desvinculado correctamente!'


@add_handlers
class GroupsBroadcast(BasicBotHandler):
    '''Sends a broadcast message to all students groups (only staff and managers)'''

    cmd = 'broadcast'

    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_permissions')

    def command(self, update, context):
        if not len(context.args):
            return '¡El mensaje no puede estar vacío!'

        groups = Group.objects.filter(~Q(telegram_group=''))

        if not len(groups):
            return 'No hay grupos a los que enviar el mensaje 😓'

        fixed_text = ' '.join(context.args).replace(r'\n', '\n')
        sent_text = '*📣 Mensaje de DAFI 📣*\n\n{}'.format(fixed_text)

        sent = 0
        fails = []

        for group in groups:
            try:
                context.bot.send_message(
                    group.telegram_group, sent_text, 'MarkdownV2'
                )

                sent += 1
            except:
                fails.append(str(group))

        msg = '`Mensaje enviado a {} grupos:`\n\n{}'.format(sent, sent_text)

        if fails:
            msg += '\n\nNo se pudo enviar a:'

            for group in fails:
                msg += '\n- {}'.format(group)

        return msg
