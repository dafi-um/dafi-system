from telegram import ParseMode

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from heart.models import Group

from .. import persistence
from ..utils import create_reply_markup

from .handlers import add_handler, CommandHandler, QueryHandler

User = get_user_model()

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
        msg = 'El periodo de elecciones está '

        if self.elections_active():
            msg += '*activo*. ¿Quieres finalizarlo?'
            btn = ('Sí, finalizar', 'elections:off')
        else:
            msg += '*inactivo*. ¿Quieres iniciarlo?'
            btn = ('Sí, iniciar', 'elections:on')

        reply_markup = create_reply_markup([
            btn,
            ('No, cancelar', 'main:okey'),
        ])

        return msg, reply_markup


class ElectionRequestMixin(ElectionsMixin, CommandHandler):
    '''Mixin to handle elections request commands'''

    chat_type = 'private'

    user_required = True

    def handle(self, update, context):
        if not self.elections_active():
            return 'No hay un periodo de elecciones activo ⚠️'

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

        group = Group.objects.filter(year=group_year, number=group_num).first()

        if not group:
            return 'El grupo especificado no existe'

        msg = (
            '*Petición para ser {}delegado*\n\n'
            'Estudios: {}\nAño: {}\nGrupo: {}\n'
            'Nombre: {}\nEmail: {}\nTelegram: @{}'
        ).format(
            prefix, group.course, group.year, group.number,
            user.get_full_name(), user.email, telegram_user.username.replace('_', '\\_')
        )

        current = group.delegate if self.is_delegate else group.subdelegate

        if current:
            msg += '\n\nActual {}delegado: {}'.format(prefix, current.get_full_name())

        query = '{}:{}.{}:{}'.format(
            telegram_user.id, group.year, group.number, int(self.is_delegate)
        )

        reply_markup = create_reply_markup([
            ('Autorizar ✅', 'elections:request:' + query),
            ('Denegar ❌', 'elections:deny:' + query),
        ])

        if not self.notify_group(msg, reply_markup, ParseMode.MARKDOWN):
            return 'No se ha podido enviar tu solicitud ⚠️'

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

    def callback(self, update, action, *args):
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

        if action != 'deny' and action != 'request':
            return

        try:
            user_id = args[0]
            group_year, group_num = args[1].split('.')
            is_delegate = bool(int(args[2]))
        except (IndexError, ValueError):
            return 'Formato de petición incorrecto'

        user = User.objects.filter(telegram_id=user_id).first()

        if not user:
            self.answer_as_reply()
            return 'El usuario no ha vinculado su cuenta'

        accepted = action == 'request'
        prefix = '' if is_delegate else 'sub'

        group = Group.objects.filter(year=group_year, number=group_num).first()

        if not group:
            return 'El grupo indicado no existe'

        if action == 'request':
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

        if accepted:
            msg = (
                'Tu petición ha sido aceptada, ahora eres {}delegado '
                'del grupo {} del año {} 🎓'
            ).format(prefix, group_num, group_year)
        else:
            msg = 'Tu petición para ser {}delegado ha sido denegada ❌'.format(prefix)

        self.context.bot.send_message(user_id, msg)

        msg = 'La solicitud de {} ha sido {} por {}'.format(
            user.get_full_name(), 'aceptada' if accepted else 'denegada',
            self.get_user().get_full_name()
        )

        if accepted:
            msg += ' ✅\n\nAhora es {}delegado del {}.{} del {}'.format(
                prefix, group.year, group.number, group.course
            )
        else:
            msg += ' ❌'

        return msg
