import itertools

from telegram.error import Unauthorized

from django.contrib.auth import get_user_model
from django.db.models import Q

from main.models import Config
from heart.models import Degree, Group, Year
from clubs.models import Club

from .handlers import add_handlers, BasicBotHandler

User = get_user_model()


@add_handlers
class GroupsList(BasicBotHandler):
    '''Returns a list of all the groups'''

    cmd = 'grupos'

    disable_web_page_preview = True

    def command(self, update, context):
        years = {degree: list(years) for degree, years in itertools.groupby(
            Year
                .objects
                .all()
                .prefetch_related('degree')
                .order_by('degree', 'year'),
            key=lambda y: y.degree.id
        )}

        groups = {degree: list(groups) for degree, groups in itertools.groupby(
            Group
                .objects
                .filter(~Q(telegram_group_link=''))
                .prefetch_related('year__degree')
                .order_by('year__degree', 'year', 'number'),
            key=lambda g: g.degree().id
        )}

        current_school_year = Config.get('current_school_year')

        msg = '*~~Grupos de Telegram{}~~*\n'.format(
            (' ' + current_school_year) if current_school_year else ''
        )

        for degree in Degree.objects.all():
            if degree.id not in groups:
                continue

            msg += '{}\n'.format(degree.name)

            if degree.is_master:
                for group in groups[degree.id]:
                    msg += ' - [{}]({})\n'.format(group.name, group.telegram_group_link)

                continue

            year_groups = {
                year: list(groups) for year, groups in
                itertools.groupby(groups[degree.id], lambda g: g.year.year)
            }

            for year in years[degree.id]:
                if year.telegram_group_link:
                    msg += ' - [{}º General]({})\n'.format(
                        year.year, year.telegram_group_link
                    )

                if year.year in year_groups:
                    for group in year_groups[year.year]:
                        msg += ' - [{}º {}]({})\n'.format(
                            group.year.year, group.name, group.telegram_group_link
                        )

                msg += '\n'

        if not self.is_group():
            return msg

        res = 'Te he enviado la lista de grupos a [nuestro chat privado]({}).'

        try:
            self.answer_private(msg)
        except Unauthorized:
            res = 'Necesito que inicies un [chat conmigo]({}) para poder enviarte la lista de grupos.'

        return res.format(self.get_bot_link())


@add_handlers
class GroupsLink(BasicBotHandler):
    '''Links a telegram group to a students group (only staff and delegates)'''

    cmd = 'vinculargrupo'

    chat_type = 'group'

    bot_admin_required = True
    user_required = True

    def command(self, update, context):
        try:
            group_id = int(context.args[0])
        except (ValueError, IndexError):
            return '**Uso**: _/vinculargrupo <ID>_\n\n'

        group = Group.objects.filter(telegram_group=update.effective_chat.id).first()

        if group:
            return (
                'Este chat de Telegram ya está vinculado al grupo {} ⚠️'
            ).format(group)

        user = self.get_user()

        query = Q(id=group_id)

        if not user.has_perm('heart.can_link_group'):
            query &= Q(delegate=user) | Q(subdelegate=user)

        group = Group.objects.filter(query).first()

        if not group:
            return 'No se ha encontrado el grupo indicado o el usuario no es un delegado'

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
