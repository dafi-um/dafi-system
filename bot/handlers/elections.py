from typing import cast

from django.db import transaction
from django.db.models import Q

from telegram import (
    ParseMode,
    Update,
)
from telegram.ext import CallbackContext

from heart.models import Group
from users.models import User

from .. import persistence
from ..utils import create_reply_markup
from .handlers import (
    BasicBotHandler,
    add_handlers,
)


ELECTIONS_KEY = 'elections_active'


@add_handlers
class ElectionsToggleHandler(BasicBotHandler):
    """Toggle the elections period.
    """

    cmd = 'elecciones'
    query_prefix = 'elections_toggle'

    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_elections')

    def elections_active(self):
        return persistence.get_item(ELECTIONS_KEY, False)

    def set_elections_active(self, value):
        persistence.set_item(ELECTIONS_KEY, value)

    def command(self, update, context):
        msg = 'El periodo de elecciones está '

        if self.elections_active():
            msg += '*activo*. ¿Quieres finalizarlo?'
            btn = ('Sí, finalizar', 'elections_toggle:off')
        else:
            msg += '*inactivo*. ¿Quieres iniciarlo?'
            btn = ('Sí, iniciar', 'elections_toggle:on')

        reply_markup = create_reply_markup([
            btn,
            ('No, cancelar', 'main:okey'),
        ])

        return msg, reply_markup

    def callback(self, update, context, action, *args):
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


@add_handlers
class ElectionRequestMixin(BasicBotHandler):
    """Mixin to handle elections request commands.
    """

    commands_available = [
        'soydelegado',
        'soysubdelegado'
    ]

    query_prefix = 'elections'

    user_required = True

    def elections_active(self):
        return persistence.get_item(ELECTIONS_KEY, False)

    def command(self, update: Update, context: CallbackContext):
        if not self.elections_active():
            return 'No hay un periodo de elecciones activo ⚠️'

        assert context.args is not None

        is_delegate = self.current_command == self.commands_available[0]

        prefix = '' if is_delegate else 'sub'

        try:
            group_id = int(context.args[0])
        except (ValueError, IndexError):
            return '**Uso**: _/soy{0}delegado <ID>_\n\n'.format(prefix)

        telegram_user = update.effective_user
        assert telegram_user is not None

        user: 'User | None' = self.get_user()
        assert user is not None

        group = Group.objects.filter(id=group_id).first()

        if not group:
            return 'El grupo especificado no existe'

        msg = (
            '*Petición para ser {}delegado*\n\n'
            'Grupo: {}\nNombre: {}\nEmail: {}\nTelegram: @{}'
        ).format(
            prefix, group, user.get_full_name(), user.email,
            telegram_user.username.replace('_', '\\_')
        )

        current = group.delegate if is_delegate else group.subdelegate

        if current:
            msg += '\n\nActual {}delegado: {}'.format(prefix, current.get_full_name())

        query = '{}:{}:{}'.format(
            telegram_user.id, group.id, int(is_delegate)
        )

        reply_markup = create_reply_markup([
            ('Autorizar ✅', 'elections:request:' + query),
            ('Denegar ❌', 'elections:deny:' + query),
        ])

        if not self.notify_group(msg, reply_markup, ParseMode.MARKDOWN):
            return 'No se ha podido enviar tu solicitud ⚠️'

        return '¡Tu solicitud se ha enviado correctamente!'

    def callback_user_filter(self, user):
        return user.has_perm('bot.can_manage_elections')

    def callback(self, update: Update, context: CallbackContext, action, *args):
        if action != 'deny' and action != 'request':
            return

        try:
            user_id = args[0]
            group_id = int(args[1])
            is_delegate = bool(int(args[2]))
        except (IndexError, ValueError):
            return 'Formato de petición incorrecto'

        user = User.objects.filter(telegram_id=user_id).first()

        if not user:
            self.answer_as_reply()
            return 'El usuario no ha vinculado su cuenta'

        accepted = action == 'request'
        prefix = '' if is_delegate else 'sub'

        group = Group.objects.filter(id=group_id).first()

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
                'Tu petición ha sido aceptada, ahora eres {}delegado del {} 🎓'
            ).format(prefix, group)
        else:
            msg = 'Tu petición para ser {}delegado ha sido denegada ❌'.format(prefix)

        context.bot.send_message(user_id, msg)

        msg = 'La solicitud de {} ha sido {} por {}'.format(
            user.get_full_name(), 'aceptada' if accepted else 'denegada',
            cast(User, self.get_user()).get_full_name()
        )

        if accepted:
            msg += ' ✅\n\nAhora es {}delegado del {}'.format(
                prefix, group
            )
        else:
            msg += ' ❌'

        return msg
