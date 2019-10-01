from os import getenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model

from .. import persistence

from .handlers import add_handler, CommandHandler, QueryHandler

User = get_user_model()

DAFI_ROOM_CODE = getenv('DAFI_ROOM_CODE', 'dafi')
DAFI_MAIN_GROUP = getenv('DAFI_MAIN_GROUP', None)

ROOM_MEMBERS_LIST = 'room_members'
ROOM_QUEUE_LIST = 'room_queue'


class RoomMixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._members = None
        self._refresh_members()

        self._queue = None
        self._refresh_queue()

    def _refresh_members(self):
        self._members = persistence.get_item(ROOM_MEMBERS_LIST, [])

    def _sync_members(self):
        persistence.set_item(ROOM_MEMBERS_LIST, self._members)

    def enter_room(self, user):
        self._refresh_members()
        self._members.append(user)
        self._sync_members()

    def leave_room(self, user):
        self._refresh_members()
        self._members.remove(user)
        self._sync_members()

    def room_empty(self):
        self._refresh_members()
        return len(self._members) == 0

    def in_room(self, user):
        self._refresh_members()
        return user in self._members

    def _refresh_queue(self):
        self._queue = persistence.get_item(ROOM_QUEUE_LIST, [])

    def _sync_queue(self):
        persistence.set_item(ROOM_QUEUE_LIST, self._queue)

    def in_queue(self, user_id):
        self._refresh_queue()
        return user_id in self._queue

    def add_to_queue(self, user_id):
        self._refresh_queue()
        self._queue.append(user_id)
        self._sync_queue()

    def get_queue(self):
        self._refresh_queue()
        return self._queue

    def clear_queue(self):
        self._queue = []
        self._sync_queue()


@add_handler('dafi')
class DafiRoom(RoomMixin, CommandHandler):
    def handle(self, update, context):
        if not context.args:
            if self.room_empty():
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        'Avísame cuando llegue alguien ✔️',
                        callback_data='dafi:notify:{}'.format(update.effective_user.id)
                    )
                ], [
                    InlineKeyboardButton('No me avises ❌', callback_data='main:okey')
                ]])

                return 'Ahora mismo no hay nadie en DAFI 😓', reply_markup

            if update.message.chat.type != 'private':
                return 'Hay alguien en DAFI ✅'

            msg = 'Hay alguien en DAFI, ¿quieres que avise de que vas?'
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton('Sí, estoy de camino 🏃🏻‍♂️', callback_data='dafi:omw')],
                [InlineKeyboardButton('No, iré luego ☕️', callback_data='main:okey')]
            ])

            return msg, reply_markup

        action = context.args[0].lower()

        if action != 'on' and action != 'off':
            return 'La opción indicada no existe'

        user = self.get_user()

        if not user or not user.has_perm('heart.can_change_room_state'):
            return 'No puedes llevar a cabo esta acción'

        if action == 'on':
            if self.in_room(user):
                return 'Ya tenía constancia de que estás en DAFI ⚠️'

            self.enter_room(user)

            msg = '@{} acaba de llegar a DAFI 🔔'.format(user.telegram_user)

            for user_id in self.get_queue():
                context.bot.send_message(user_id, msg)

            self.clear_queue()

            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton('Me voy 💤', callback_data='dafi:off')
            ]])

            return 'He anotado que estás DAFI ✅', reply_markup

        else:
            if not self.in_room(user):
                return 'No sabía que estabas en DAFI ⚠️'

            self.leave_room(user)

            return 'He anotado que has salido de DAFI ✅'


@add_handler('dafi')
class DafiCallback(RoomMixin, QueryHandler):
    def handle(self, update, context):
        query = update.callback_query
        parts = query.data.replace('dafi:', '').split(':')
        action = parts[0]

        if action == 'omw':
            if self.room_empty():
                return 'Ahora mismo no hay nadie en DAFI 😓'

            if DAFI_MAIN_GROUP:
                text = '¡{} está de camino a DAFI!'.format(query.from_user.name)
                context.bot.sendMessage(DAFI_MAIN_GROUP, text=text)

            return 'Hecho, les he avisado 😉'
        elif action == 'notify':
            self.add_to_queue(update.effective_user.id)

            return 'Hecho, te avisaré 😉'
        elif action == 'off':
            user = self.get_user()

            if not user:
                return 'No he encontrado una cuenta para tu usuario ⚠️'

            if not self.in_room(user):
                return 'No sabía que estabas en DAFI ⚠️'

            self.leave_room(user)

            return 'He anotado que has salido de DAFI  ✅'
