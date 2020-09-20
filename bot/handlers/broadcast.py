import itertools

from telegram import ParseMode

from django.db.models import Q

from heart.models import Group, Year
from clubs.models import Club

from ..utils import create_reply_markup

from .handlers import add_handlers, BasicBotHandler

TARGET_GROUPS = 'groups'
TARGET_CLUBS = 'clubs'

BROACDAST_TARGETS = [
    TARGET_GROUPS,
    TARGET_CLUBS
]

pending_broadcasts = {}


class Broadcast():
    '''Broadcast helper'''

    def __init__(self, text):
        self.text = text
        self.msg = None
        self.chats = set()

    def add_chat(self, title, id):
        self.chats.add((title, id))


@add_handlers
class BroadcastHandler(BasicBotHandler):
    '''Sends a broadcast message (only staff and managers)'''

    cmd = 'broadcast'
    query_prefix = 'broadcast'

    user_required = True

    def user_filter(self, user):
        return user.has_perm('bot.can_manage_permissions')

    def callback_user_filter(self, user):
        return user.has_perm('bot.can_manage_permissions')

    def command(self, update, context):
        message = update.effective_message
        reply = message.reply_to_message

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
                ' - `target` disponibles: `' + ' '.join(BROACDAST_TARGETS) + '`\n'
                ' - Separa los `target` con `;`\n'
                ' - Separa los IDs con `,`\n'
                ' - El ID para un grupo es: `año` ó `año.grupo` (ej: `groups:1.2` para 1º G2)\n'
                ' - Un `target` sin IDs indica todos los grupos de ese tipo\n'
                '\n'
                'Ejemplo para todos los grupos de primer y segundo curso, y el club _test_:\n'
                '`/broadcast groups:1,2;clubs:test`'
            )
            return

        if not len(reply.text_markdown):
            message.reply_text('¡El mensaje no puede estar vacío!')
            return

        bcast_obj = Broadcast(
            '*📣 Mensaje de DAFI 📣*\n\n' + reply.text_markdown
        )

        msg = 'El mensaje se enviará a los siguientes grupos:\n\n'

        targets = BROACDAST_TARGETS

        if len(context.args):
            targets = set()

            for target in context.args[0].split(';'):
                targets.add(target)

        for target in targets:
            args = target.split(':')

            target_type = args[0]
            ids = None if len(args) == 1 else args[1]

            if target_type == TARGET_GROUPS:
                query = Q()

                if ids:
                    for pair in ids.split(','):
                        if '.' in pair:
                            year, group = pair.split('.')

                            query |= Q(year=year, number=group)
                        else:
                            query |= Q(year=pair)

                groups = Group.objects.filter(~Q(telegram_group='') & query)

                for group in groups:
                    title = '[{} {}º {}]'.format(group.course, group.year, group.name)

                    bcast_obj.add_chat(title, group.telegram_group)
                    msg += ' - {}\n'.format(title)
            elif target_type == TARGET_CLUBS:
                query = Q()

                if ids:
                    for club in ids.split(','):
                        query |= Q(slug=club)

                clubs = Club.objects.filter(~Q(telegram_group='') & query)

                for club in clubs:
                    bcast_obj.add_chat(club.name, club.telegram_group)
                    msg += ' - {}\n'.format(club.name)
            else:
                message.reply_markdown(
                    '¡`{}` no es un _target_ válido!'.format(target_type)
                )
                return

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

    def callback(self, update, context, action, *args):
        if not len(args):
            return

        bcast_id = args[0]

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
            except:
                errors.append(chat_title)

        msg = '¡Mensaje enviado con éxito a {} chats!\n'.format(
            len(bcast_obj.chats) - len(errors)
        )

        if errors:
            msg += '\n\nErrores:\n'

            for error in errors:
                msg += ' - {}\n'.format(error)

        return msg
