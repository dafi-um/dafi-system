from django.db.models import Q

from telegram import (
    Message,
    ParseMode,
    TelegramError,
    Update,
)
from telegram.ext import CallbackContext

from clubs.models import Club
from heart.models import Group
from users.models import User

from ..utils import create_reply_markup
from .handlers import (
    BasicBotHandler,
    add_handlers,
)


TARGET_GROUPS = 'groups'
TARGET_CLUBS = 'clubs'

BROADCAST_TARGETS = [
    TARGET_GROUPS,
    TARGET_CLUBS
]


class Broadcast():
    """Broadcast helper.
    """

    def __init__(self, text: str):
        self.text = text
        self.msg: 'Message | None' = None
        self.chats: set[tuple[str, str]] = set()

    def add_chat(self, title: str, id: str) -> None:
        self.chats.add((title, id))


pending_broadcasts: dict[str, Broadcast] = {}


@add_handlers
class BroadcastHandler(BasicBotHandler):
    """Sends a broadcast message (only staff and managers).
    """

    cmd = 'broadcast'
    query_prefix = 'broadcast'

    user_required = True

    def user_filter(self, user: User):
        return user.has_perm('bot.can_manage_permissions')

    def callback_user_filter(self, user: User):
        return user.has_perm('bot.can_manage_permissions')

    def command(self, update: Update, context: CallbackContext):
        message = update.effective_message
        assert message is not None

        reply: Message = message.reply_to_message

        if not reply:
            message.reply_markdown(
                '*Ayuda de Broadcast*\n'
                '\n'
                '1. Escribe un mensaje con el texto deseado\n'
                '2. Responde a ese mensaje con `/broadcast [destinos]`\n'
                '3. Selecciona _Sí_ para enviar o _Cancelar_ para lo contrario\n'
                '\n'
                '\n'
                'Formato del parámetro *opcional* `destinos`:\n'
                '`target:id1,id2;target2:id1;target3`\n'
                '\n'
                ' - Por defecto un mensaje se enviará a todos los grupos conocidos\n'
                ' - `target` disponibles: `' + ' '.join(BROADCAST_TARGETS) + '`\n'
                ' - Separa los `target` con `;`\n'
                ' - Separa los IDs con `,`\n'
                ' - El ID para un grupo es: `grado.año.grupo` (ej: `groups:GII.1.2` para GII 1º G2)\n'
                ' - Las dos últimas partes del ID de un grupo son opcionales\n'
                ' - Un `target` sin IDs indica todos los grupos de ese tipo\n'
                '\n'
                'Ejemplo para todos los grupos de primer y segundo curso de GII, y el club _test_:\n'
                '`/broadcast groups:GII.1,GII.2;clubs:test`'
            )
            return

        if not len(reply.text_markdown):
            message.reply_text('¡El mensaje no puede estar vacío!')
            return

        bcast_obj = Broadcast(
            '*📣 Mensaje de DAFI 📣*\n\n' + reply.text_markdown
        )

        msg = 'El mensaje se enviará a los siguientes grupos:\n\n'

        assert context.args is not None

        targets = context.args[0].split(';') if len(context.args) else BROADCAST_TARGETS

        for target in targets:
            target_type, _, filters = target.partition(':')

            query = Q()

            if target_type == TARGET_GROUPS:
                if filters:
                    for filter in filters.split(','):
                        items = filter.split('.')

                        subquery = Q(year__degree=items[0])

                        if len(items) > 1:
                            subquery &= Q(year__year=items[1])

                        if len(items) > 2:
                            subquery &= Q(number=items[2])

                        query |= subquery

                groups = Group.objects.filter(~Q(telegram_group='') & query)

                for group in groups:
                    title = str(group)

                    bcast_obj.add_chat(title, group.telegram_group)
                    msg += ' - {}\n'.format(title)
            elif target_type == TARGET_CLUBS:
                if filters:
                    for slug in filters.split(','):
                        query |= Q(slug=slug)

                clubs = Club.objects.filter(~Q(telegram_group='') & query)

                for club in clubs:
                    bcast_obj.add_chat(club.name, club.telegram_group)
                    msg += ' - {}\n'.format(club.name)

        pending_broadcasts[str(message.message_id)] = bcast_obj

        reply_markup = create_reply_markup([
            ('Enviar ✅', 'send:' + str(message.message_id)),
            ('Cancelar ❌', 'cancel:' + str(message.message_id)),
        ], prefix=self.query_prefix)

        sent_msg = message.reply_markdown(bcast_obj.text)

        bcast_obj.msg = sent_msg

        sent_msg.reply_markdown(msg, reply_markup=reply_markup)

        # TODO: Remove when the handlers API is updated to ignore returned values
        self.msg = None

    def callback(self, update: Update, context: CallbackContext, action: str, *args):
        if not len(args):
            return

        bcast_id: str = args[0]

        if bcast_id not in pending_broadcasts:
            # TODO: Update
            return 'El broadcast no se ha encontrado', None

        bcast_obj = pending_broadcasts[bcast_id]

        if action == 'cancel':
            if bcast_obj.msg:
                bcast_obj.msg.delete()

            pending_broadcasts.pop(bcast_id)

            # TODO: Update
            return 'Operación cancelada.'

        errors = []

        for chat_title, chat_id in bcast_obj.chats:
            try:
                context.bot.send_message(
                    chat_id, bcast_obj.text, ParseMode.MARKDOWN
                )
            except TelegramError:
                errors.append(chat_title)

        msg = '¡Mensaje enviado con éxito a {} chats!\n'.format(
            len(bcast_obj.chats) - len(errors)
        )

        if errors:
            msg += '\n\nErrores:\n'

            for error in errors:
                msg += ' - {}\n'.format(error)

        return msg
