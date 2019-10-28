from os import getenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model

from .. import persistence

from .handlers import add_handler, CommandHandler, QueryHandler

User = get_user_model()

DAFI_MAIN_GROUP = getenv('DAFI_MAIN_GROUP', None)

ROOM_MEMBERS_LIST = 'room_members'
ROOM_QUEUE_LIST = 'room_queue'

ALT_ROOM_MEMBERS_LIST = 'alt_room_members'
ALT_ROOM_QUEUE_LIST = 'alt_room_queue'
ALT_ROOM_GROUP = getenv('ALT_ROOM_GROUP', None)


@add_handler('dafi')
class DafiRoom(CommandHandler):
    def handle(self, update, context):
        members = persistence.get_item(ROOM_MEMBERS_LIST, [])

        if not context.args:
            if not members:
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        'Avísame cuando llegue alguien ✔️',
                        callback_data='dafi:notify:{}'.format(update.effective_user.id)
                    )
                ], [
                    InlineKeyboardButton('No me avises ❌', callback_data='main:okey')
                ]])

                return 'Ahora mismo no hay nadie en DAFI 😓', reply_markup

            msg = '🏠 *DAFI* 🎓\nEn la delegación está{}...\n'.format('n' if len(members) > 1 else '')
            reply_markup = None

            for user in members:
                msg += '\n[{}](tg://user?id={})'.format(user.get_full_name(), user.telegram_id)

            if update.message.chat.type == 'private':
                msg += '\n\n¿Quieres que avise de que vas?'
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton('Sí, estoy de camino 🏃🏻‍♂️', callback_data='dafi:omw')],
                    [InlineKeyboardButton('No, iré luego ☕️', callback_data='main:okey')]
                ])

            return msg, reply_markup

        action = context.args[0].lower()

        if action != 'on' and action != 'off':
            return 'La opción indicada no existe'

        user = self.get_user()

        if not user or not user.has_perm('bot.can_change_room_state'):
            return 'No puedes llevar a cabo esta acción'

        if action == 'on':
            if user in members:
                return 'Ya tenía constancia de que estás en DAFI ⚠️'

            members.append(user)

            msg = '@{} acaba de llegar a DAFI 🔔'.format(user.telegram_user)

            queue = persistence.get_item(ROOM_QUEUE_LIST, [])

            if queue:
                for user_id in queue:
                    context.bot.send_message(user_id, msg)

                queue.clear()

            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton('Me voy 💤', callback_data='dafi:off')
            ]])

            return 'He anotado que estás DAFI ✅', reply_markup

        else:
            if user not in members:
                return 'No sabía que estabas en DAFI ⚠️'

            members.remove(user)

            return 'He anotado que has salido de DAFI ✅'


@add_handler('dafi')
class DafiCallback(QueryHandler):
    def handle(self, update, context):
        query = update.callback_query
        _, action, *args = query.data.split(':')

        members = persistence.get_item(ROOM_MEMBERS_LIST, [])
        queue = persistence.get_item(ROOM_QUEUE_LIST, [])

        if action == 'omw':
            if not members:
                return 'Ahora mismo no hay nadie en DAFI 😓'

            if DAFI_MAIN_GROUP:
                text = '¡{} está de camino a DAFI!'.format(query.from_user.name)
                context.bot.sendMessage(DAFI_MAIN_GROUP, text=text)

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
                return 'No sabía que estabas en DAFI ⚠️'

            members.remove(user)

            return 'He anotado que has salido de DAFI ✅'


@add_handler('repro')
class AltRoomHandler(CommandHandler):
    def handle(self, update, context):
        members = persistence.get_item(ALT_ROOM_MEMBERS_LIST, [])

        if not context.args:
            if not members:
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        'Avísame cuando llegue alguien ✔️',
                        callback_data='alt_room:notify:{}'.format(update.effective_user.id)
                    )
                ], [
                    InlineKeyboardButton('No me avises ❌', callback_data='main:okey')
                ]])

                return 'Ahora mismo no hay nadie en reprografía 😓', reply_markup

            msg = '🏠 *REPROGRAFÍA* 🎓\nEn reprografía está{}...\n'.format(
                'n' if len(members) > 1 else ''
            )

            reply_markup = None

            for user in members:
                msg += '\n[{}](tg://user?id={})'.format(user.get_full_name(), user.telegram_id)

            if update.message.chat.type == 'private':
                msg += '\n\n¿Quieres que avise de que vas?'
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        'Sí, estoy de camino 🏃🏻‍♂️', callback_data='alt_room:omw'
                    )],

                    [InlineKeyboardButton('No, iré luego ☕️', callback_data='main:okey')]
                ])

            return msg, reply_markup

        action = context.args[0].lower()

        if action != 'on' and action != 'off':
            return 'La opción indicada no existe'

        user = self.get_user()

        if not user or not user.has_perm('bot.can_change_alt_room_state'):
            return 'No puedes llevar a cabo esta acción.'

        if action == 'on':
            if user in members:
                return 'Ya tenía constancia de que estás en reprografía ⚠️'

            members.append(user)

            msg = '@{} acaba de llegar a reprografía 🔔'.format(user.telegram_user)

            queue = persistence.get_item(ALT_ROOM_QUEUE_LIST, [])

            if queue:
                for user_id in queue:
                    context.bot.send_message(user_id, msg)

                queue.clear()

            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton('Me voy 💤', callback_data='alt_room:off')
            ]])

            return 'He anotado que estás reprografía ✅', reply_markup

        else:
            if user not in members:
                return 'No sabía que estabas en reprografía ⚠️'

            members.remove(user)

            return 'He anotado que has salido de reprografía ✅'


@add_handler('alt_room')
class AltRoomCallback(QueryHandler):
    def handle(self, update, context):
        query = update.callback_query
        _, action, *args = query.data.split(':')

        members = persistence.get_item(ALT_ROOM_MEMBERS_LIST, [])
        queue = persistence.get_item(ALT_ROOM_QUEUE_LIST, [])

        if action == 'omw':
            if not members:
                return 'Ahora mismo no hay nadie en reprografía 😓'

            if ALT_ROOM_GROUP:
                text = '¡{} está de camino a reprografía!'.format(query.from_user.name)
                context.bot.sendMessage(ALT_ROOM_GROUP, text=text)

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
                return 'No sabía que estabas en reprografía ⚠️'

            members.remove(user)

            return 'He anotado que has salido de reprografía ✅'
