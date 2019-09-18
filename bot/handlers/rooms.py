from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from django.contrib.auth import get_user_model

from heart.models import Room

from .handlers import add_handler, add_query_handler

User = get_user_model()

DAFI_ROOM_CODE = 'dafi'
DAFI_MAIN_GROUP = -375391840


@add_query_handler('dafi')
def dafi_callback(update, context):
    query = update.callback_query
    action = query.data.replace('dafi:', '')

    if action == 'later':
        return '¡De acuerdo!'

    room = Room.objects.filter(code=DAFI_ROOM_CODE).first()

    if not room:
        return '⚠️⚠️\n¡¡La sala no existe en la base de datos!!'

    members = room.get_members()

    if action == 'omw':
        if not members:
            return 'Ahora mismo no hay nadie en DAFI 😓'

        text = '¡{} está de camino a DAFI!'.format(query.from_user.name)
        context.bot.sendMessage(DAFI_MAIN_GROUP, text=text)

        return 'Hecho, les he avisado 😉'
    elif action == 'off':
        user = User.objects.filter(telegram_id=query.from_user.id).first()

        if not user:
            return 'No he encontrado una cuenta para tu usuario ⚠️'

        if user in members:
            room.remove_member(user)

        return 'He anotado que has salido de DAFI.'

@add_handler('dafi')
def dafi_room(update, context):
    room = Room.objects.filter(code=DAFI_ROOM_CODE).first()

    if not room:
        return '⚠️⚠️\n¡¡La sala no existe en la base de datos!!'

    members = room.get_members()

    if not context.args:
        if update.message.chat.type != 'private':
            return 'Este comando solamente puede utilizarse en chats privados'

        if not members:
            return 'Ahora mismo no hay nadie en DAFI 😓'

        msg = 'Hay alguien en DAFI, ¿quieres que avise de que vas?'
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('Sí, estoy de camino 🏃🏻‍♂️', callback_data='dafi:omw')],
            [InlineKeyboardButton('No, iré luego ☕️', callback_data='dafi:later')]
        ])

        return msg, reply_markup

    action = context.args[0].lower()

    if action != 'on' and action != 'off':
        return 'La opción indicada no existe'

    message = update.effective_message
    user = User.objects.filter(telegram_id=message.from_user.id).first()

    if not user or not user.has_perm('users.change_room_state'):
        return 'No puedes llevar a cabo esta acción'

    room = Room.objects.get()
    members = room.get_members()

    if action == 'on':
        if user in members:
            return 'Ya tenía constancia de que estás en DAFI ⚠️'

        room.add_member(user)

        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('Me voy 💤', callback_data='dafi:off')
        ]])

        return 'He anotado que estás DAFI ✅', reply_markup

    else:
        if user not in members:
            return 'No sabía que estabas en DAFI ⚠️'

        room.remove_member(user)
        return 'He anotado que has salido de DAFI ✅'
