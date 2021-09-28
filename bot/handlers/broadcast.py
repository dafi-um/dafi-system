from enum import Enum

from django.db.models import Q

from telegram import (
    Message,
    ParseMode,
    TelegramError,
    Update,
)
from telegram.ext import CallbackContext

from bot.utils import (
    create_reply_markup,
    prepare_callback,
)
from clubs.models import Club
from heart.models import Group

from ..decorators import (
    auth_required,
    auto_answer_query,
)


class BroadcastTargets(str, Enum):

    CLUBS = 'clubs'
    GROUPS = 'groups'

    @classmethod
    def get_targets(cls) -> list[str]:
        return [item.value for item in cls.__members__.values()]


class BroadcastMessage():
    """Broadcast helper.
    """

    def __init__(self, text: str):
        self.text = text
        self.msg: 'Message | None' = None
        self.chats: set[tuple[str, str]] = set()

    def add_chat(self, title: str, id: str) -> None:
        self.chats.add((title, id))


USAGE_MSG = (
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
    ' - `target` disponibles: `' + ' '.join(BroadcastTargets.get_targets()) + '`\n'
    ' - Separa los `target` con `;`\n'
    ' - Separa los IDs con `,`\n'
    ' - El ID para un grupo es: `grado.año.grupo` (ej: `groups:GII.1.2` para GII 1º G2)\n'
    ' - Las dos últimas partes del ID de un grupo son opcionales\n'
    ' - Un `target` sin IDs indica todos los grupos de ese tipo\n'
    '\n'
    'Ejemplo para todos los grupos de primer y segundo curso de GII, y el club _test_:\n'
    '`/broadcast groups:GII.1,GII.2;clubs:test`'
)


@auth_required('bot.can_manage_permissions')
def cmd_broadcast(update: Update, context: CallbackContext[dict, dict, dict], *_) -> None:
    assert context.args is not None
    assert update.effective_message is not None

    reply: 'Message | None' = update.effective_message.reply_to_message

    if not reply:
        update.effective_message.reply_markdown(USAGE_MSG)
        return

    if not len(reply.text_markdown):
        update.effective_message.reply_text('¡El mensaje no puede estar vacío!')
        return

    bcast_obj = BroadcastMessage(
        '*📣 Mensaje de DAFI 📣*\n\n' + reply.text_markdown
    )

    info_msg = 'El mensaje se enviará a los siguientes grupos:\n\n'

    targets = context.args[0].split(';') if len(context.args) else BroadcastTargets.get_targets()

    for target in targets:
        target_type, _, filters = target.partition(':')

        query = Q()

        if target_type == BroadcastTargets.GROUPS:
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
                info_msg += f' - {title}\n'
        elif target_type == BroadcastTargets.CLUBS:
            if filters:
                for slug in filters.split(','):
                    query |= Q(slug=slug)

            clubs = Club.objects.filter(~Q(telegram_group='') & query)

            for club in clubs:
                bcast_obj.add_chat(club.name, club.telegram_group)
                info_msg += f' - {club.name}\n'

    if not len(bcast_obj.chats):
        update.effective_message.reply_text(
            'No se encontraron receptores para los destinos indicados ⚠️'
        )
        return

    context.bot_data['broadcast' + str(update.effective_message.message_id)] = bcast_obj

    reply_markup = create_reply_markup([
        ('Enviar ✅', 'broadcast:send:' + str(update.effective_message.message_id)),
        ('Cancelar ❌', 'broadcast:cancel:' + str(update.effective_message.message_id)),
    ])

    sent_msg = update.effective_message.reply_markdown(bcast_obj.text)
    sent_msg.reply_markdown(info_msg, reply_markup=reply_markup)

    bcast_obj.msg = sent_msg


@auto_answer_query
@auth_required('bot.can_manage_permissions')
def callback_broadcast(update: Update, context: CallbackContext[dict, dict, dict], *_) -> None:
    query, action, args = prepare_callback(update)

    if not len(args):
        return

    try:
        bcast_obj: BroadcastMessage = context.bot_data.pop('broadcast' + args[0])
    except KeyError:
        query.edit_message_text(
            'La información del envío no se ha encontrado ⚠️'
        )
        return

    if action == 'cancel':
        if bcast_obj.msg:
            bcast_obj.msg.delete()

        query.edit_message_text(
            '¡Operación cancelada!'
        )
        return

    errors: list[str] = []

    for chat_title, chat_id in bcast_obj.chats:
        try:
            context.bot.send_message(
                chat_id,
                bcast_obj.text,
                parse_mode=ParseMode.MARKDOWN
            )
        except TelegramError:
            errors.append(chat_title)

    msg = 'Mensaje enviado con éxito a {} chats ✅\n'.format(
        len(bcast_obj.chats) - len(errors)
    )

    if errors:
        msg += '\n\nErrores:\n'

        for error in errors:
            msg += ' - {}\n'.format(error)

    query.edit_message_text(msg)
