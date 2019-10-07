from os import getenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from heart.models import Group

from .. import persistence

from .handlers import add_handler, CommandHandler, QueryHandler

User = get_user_model()

DAFI_MAIN_GROUP = getenv('DAFI_MAIN_GROUP', None)
ELECTIONS_KEY = 'elections_active'


class ElectionsMixin():
    def elections_active(self):
        return persistence.get_item(ELECTIONS_KEY, False)

    def set_elections_active(self, value):
        persistence.set_item(ELECTIONS_KEY, value)


@add_handler('elecciones')
class ElectionsToggleHandler(ElectionsMixin, CommandHandler):
    '''Toggle the elections period'''

    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_elections')

    def handle(self, update, context):
        if self.elections_active():
            status = '*activo*. ¿Quieres finalizarlo?'
            btn = InlineKeyboardButton('Sí, finalizar', callback_data='elections:off')
        else:
            status = '*inactivo*. ¿Quieres iniciarlo?'
            btn = InlineKeyboardButton('Sí, iniciar', callback_data='elections:on')

        msg = 'El periodo de elecciones está ' + status

        reply_markup = InlineKeyboardMarkup([[
            btn,
            InlineKeyboardButton('No, cancelar', callback_data='main:okey'),
        ]])

        return msg, reply_markup


class ElectionRequestMixin(ElectionsMixin, CommandHandler):
    '''Mixin to handle elections request commands'''

    chat_type = 'private'

    user_required = True

    def handle(self, update, context):
        if not self.elections_active():
            return 'No hay un periodo de elecciones activo ⚠️'

        if not DAFI_MAIN_GROUP:
            return '⚠️ No se pudo procesar tu solicitud ⚠️\nContacta con los responsables de la Delegación.'

        prefix = '' if self.is_delegate else 'sub'

        try:
            group_year, group_num = [int(x) for x in context.args[0].split('.')]
        except (ValueError, IndexError):
            return (
                '**Uso**: _/soy{0}delegado <curso>.<grupo>_\n\n'
                '**Ej**: para el grupo 1 de tercero usa `/soy{0}delegado 3.1`'
            ).format(prefix)

        telegram_user = update.effective_user
        user = self.get_user()

        g_msg = (
            '*Petición para ser {}delegado*\n\n'
            'Año: {}\nGrupo: {}\nNombre: {}\nEmail: {}\nTelegram: @{}'
        ).format(
            prefix, group_year, group_num,
            user.get_full_name(), user.email, telegram_user.username
        )

        query = 'elections:request:{}:{}.{}:{}'.format(
            telegram_user.id, group_year, group_num, int(self.is_delegate)
        )

        g_reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('Autorizar ✅', callback_data=query),
            InlineKeyboardButton('Denegar ❌', callback_data='main:okey'),
        ]])

        context.bot.send_message(
            DAFI_MAIN_GROUP, g_msg, ParseMode.MARKDOWN, reply_markup=g_reply_markup
        )

        return '¡Tu solicitud se ha enviado correctamente!'


@add_handler('soydelegado')
class ElectionsToggleHandler(ElectionRequestMixin):
    '''Starts a delegate request'''

    is_delegate = True


@add_handler('soysubdelegado')
class ElectionsToggleHandler(ElectionRequestMixin):
    '''Starts a subdelegate request'''

    is_delegate = False


@add_handler('elections')
class ElectionsToggleCallback(ElectionsMixin, QueryHandler):
    '''Handles elections requests buttons'''

    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_elections')

    def handle(self, update, context):
        query = update.callback_query
        _, action, *args = query.data.split(':')

        if action == 'on':
            if self.elections_active():
                return 'El periodo de elecciones ya está activo.'

            self.set_elections_active(True)

            return 'Ahora el periodo de elecciones está activo ✅'
        elif action == 'off':
            if not self.elections_active():
                return 'El periodo de elecciones ya está inactivo.'

            self.set_elections_active(False)

            return 'Ahora el periodo de elecciones está inactivo ✅'
        elif action == 'request':
            if len(args) != 3:
                return 'Formato de petición incorrecto'

            user_id = args[0]
            user = User.objects.filter(telegram_id=user_id).first()

            if not user:
                return 'El usuario no ha vinculado su cuenta'

            try:
                group_year, group_num = args[1].split('.')
            except (IndexError, ValueError):
                return 'Formato de petición incorrecto'

            group = Group.objects.filter(year=group_year, number=group_num).first()

            if not group:
                return 'El grupo indicado no existe'

            is_delegate = bool(int(args[2]))
            prefix = '' if is_delegate else 'sub'

            query = Q(delegate=user) | Q(subdelegate=user)

            with transaction.atomic():
                groups = Group.objects.filter(query)

                for g in groups:
                    if g.delegate == user:
                        g.delegate = None
                    else:
                        g.subdelegate = None

                    g.save()

            if is_delegate:
                group.delegate = user
            else:
                group.subdelegate = user

            group.save()

            context.bot.send_message(user_id,
                'Tu petición ha sido aceptada, ahora eres {}delegado '
                'del grupo {} del año {} 🎓'.format(prefix, group_num, group_year)
            )

            return 'Petición aceptada, ahora {} es {}delegado del {}.{}'.format(
                user.get_full_name(), prefix, group_year, group_num
            )
