import schedule

from telegram import ParseMode

from django.contrib.auth import get_user_model

from .. import persistence
from ..jobs import add_job
from ..utils import create_reply_markup

from .handlers import add_handlers, BasicBotHandler, Config

User = get_user_model()

ROOM_MEMBERS_LIST = 'room_members'
ROOM_QUEUE_LIST = 'room_queue'

ALT_ROOM_MEMBERS_LIST = 'alt_room_members'
ALT_ROOM_QUEUE_LIST = 'alt_room_queue'


@add_handlers
class DafiRoom(BasicBotHandler):
    '''Main room handler'''

    cmd = 'dafi'
    query_prefix = 'dafi'

    members_list_key = ROOM_MEMBERS_LIST
    queue_list_key = ROOM_QUEUE_LIST

    management_permission = 'bot.can_change_room_state'

    room_name = 'DAFI'
    room_name_long = 'la delegación'

    OPTION_ON = 'on'
    OPTION_OFF = 'off'
    OPTION_LIST = 'lista'

    OPTIONS = (OPTION_ON, OPTION_OFF, OPTION_LIST)

    def command(self, update, context):
        members = persistence.get_item(self.members_list_key, [])

        if not context.args:
            if not members:
                reply_markup = create_reply_markup(
                    [(
                        'Avísame cuando llegue alguien ✔️',
                        '{}:notify:{}'.format(self.query_prefix, update.effective_user.id)
                    )],
                    [('No me avises ❌', 'main:okey')]
                )

                return 'Ahora mismo no hay nadie en {} 😓'.format(self.room_name), reply_markup

            msg = '🏠 *{}* 🎓\nEn {} está{}...\n'.format(
                self.room_name, self.room_name_long, 'n' if len(members) > 1 else ''
            )

            reply_markup = None

            for user in members:
                msg += '\n[{}](tg://user?id={})'.format(user.get_full_name(), user.telegram_id)

            if update.message.chat.type == 'private':
                msg += '\n\n¿Quieres que avise de que vas?'
                reply_markup = create_reply_markup(
                    [('Sí, estoy de camino 🏃🏻‍♂️', '{}:omw'.format(self.query_prefix))],
                    [('No, iré luego ☕️', 'main:okey')],
                )

            return msg, reply_markup

        action = context.args[0].lower()

        if action not in self.OPTIONS:
            return 'La opción indicada no existe'

        user = self.get_user()

        if not user or not user.has_perm(self.management_permission):
            return 'No puedes llevar a cabo esta acción'

        if action == self.OPTION_ON:
            if user in members:
                return 'Ya tenía constancia de que estás en {} ⚠️'.format(self.room_name)

            members.append(user)

            msg = '@{} acaba de llegar a {} 🔔'.format(
                user.telegram_user, self.room_name
            )

            queue = persistence.get_item(self.queue_list_key, [])

            if queue:
                for user_id in queue:
                    try:
                        context.bot.send_message(user_id, msg)
                    except:
                        # So many errors can occur here but it's a simple
                        # notification, so we'll just ignore a failed one
                        pass

                queue.clear()

            reply_markup = create_reply_markup([
                ('Me voy 💤', '{}:off'.format(self.query_prefix))
            ])

            return 'He anotado que estás en DAFI ✅'.format(self.room_name), reply_markup

        elif action == self.OPTION_OFF:
            if user not in members:
                return 'No sabía que estabas en {} ⚠️'.format(self.room_name)

            members.remove(user)

            return 'He anotado que has salido de {} ✅'.format(self.room_name)

        elif action == self.OPTION_LIST:
            queue = persistence.get_item(self.queue_list_key, [])

            if not queue:
                return 'No hay nadie esperando para ir a {} ✅'.format(self.room_name)

            users = User.objects.filter(telegram_id__in=queue)

            msg = 'Usuarios esperando para ir a {}:\n'.format(self.room_name)

            for user in users:
                msg += '\n[{}](tg://user?id={})'.format(
                    user.get_full_name(), user.telegram_id
                )

            diff = len(queue) - len(users)

            if diff == 1:
                msg += '\n\nHay otra persona más esperando, pero no es un usuario registrado.'
            elif diff > 1:
                msg += (
                    '\n\nHay otras {} personas más esperando, '
                    'pero no son usuarios registrados.'
                ).format(diff)

            return msg

    def callback(self, update, context, action, *args):
        members = persistence.get_item(self.members_list_key, [])
        queue = persistence.get_item(self.queue_list_key, [])

        if action == 'omw':
            if not members:
                return 'Ahora mismo no hay nadie en {} 😓'.format(self.room_name)

            text = '¡{} está de camino a {}!'.format(
                update.effective_user.name, self.room_name
            )

            if not self.notify_group(text):
                return 'No he podido avisarles 😓'

            return 'Hecho, les he avisado 😉'
        elif action == 'notify':
            user_id = update.effective_user.id

            if user_id not in queue:
                queue.append(user_id)

            return 'Hecho, te avisaré 😉'
        elif action == 'off':
            user = self.get_user()

            if not user:
                return 'No he encontrado una cuenta para tu usuario ⚠️'

            if user not in members:
                return 'No sabía que estabas en {} ⚠️'.format(self.room_name)

            members.remove(user)

            return 'He anotado que has salido de {} ✅'.format(self.room_name)


@add_handlers
class AltRoomHandler(DafiRoom):
    '''Alternative room handler'''

    cmd = 'repro'
    query_prefix = 'repro'

    members_list_key = ALT_ROOM_MEMBERS_LIST
    queue_list_key = ALT_ROOM_QUEUE_LIST

    management_permission = 'bot.can_change_alt_room_state'

    room_name = 'Reprografía'
    room_name_long = 'reprografía'


@add_job(schedule.every().day.at('21:10'))
def remind_remaining_room_members(bot):
    msg_pat = (
        '¡Oye! Parece que te has dejado activado el '
        '`/{0}` y la facultad ya ha cerrado, quizás deberías '
        'ejecutar `/{0} off` para salir.'
    )

    commands = [
        (ROOM_MEMBERS_LIST, 'dafi'),
        (ALT_ROOM_MEMBERS_LIST, 'repro'),
    ]

    for list_key, cmd in commands:
        members = persistence.get_item(list_key, [])

        msg = msg_pat.format(cmd)

        for member in members:
            bot.send_message(
                member.telegram_id, msg, parse_mode=ParseMode.MARKDOWN
            )
