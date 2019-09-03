from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler, run_async

from django.contrib.auth import get_user_model
from heart.models import Room


DAFI_MAIN_GROUP = -1001247574203
User = get_user_model()


@run_async
def dafi_callback(update, context):
    bot = context.bot
    query = update.callback_query
    telegramUser = query.from_user
    chatID = query.message.chat_id
    message = query.message.text
    query.answer()

    user = User.objects.get(telegram_id=telegramUser.id)
    r = Room.objects.get()
    members = r.get_members()

    data = query.data.split('-')

    if data[1] == 'omw':
        if members:
            text = '{} está de camino a DAFI! 🦔'.format(telegramUser.name)
            editText = 'Hecho, les he avisado 😉'
            try: bot.sendMessage(DAFI_MAIN_GROUP, text=text)
            except: pass
        else:
            editText = 'Ahora mismo no hay nadie en DAFI 😓'
        query.edit_message_text(editText)

    elif data[1] == 'later':
        query.edit_message_text('¡De acuerdo! ☕️')

    elif data[1] == 'off':
        if user not in members:
            query.edit_message_text('No sabía que estabas en DAFI ⚠️')
        else:
            query.edit_message_text('He anotado que has salido de DAFI 💤')
            r.remove_member(user)



@run_async
def dafi_room(update, context):
    bot = context.bot
    args = context.args[0].lower() if context.args else None
    telegramUser = update.effective_message.from_user
    chatID = update.effective_message.chat_id
    priv = chatID > 0

    try:
        user = User.objects.get(telegram_id=telegramUser.id)
        allowed = user.has_perm('users.change_room_state')
    except:
        user = allowed = None


    r = Room.objects.get()
    members = r.get_members()

    if allowed and args:
        if args == 'on':
            if user in members:
                bot.sendMessage(chatID,
                                'Ya tenía constancia de que estás en DAFI ⚠️')
                return
            r.add_member(user)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Me voy 💤", callback_data='dafi-off')]
            ])
            bot.sendMessage(chatID, 'He anotado que estás DAFI ✅',
                            reply_markup=keyboard)
            # TODO: Si es el primer usuario que ha entrado, notificar
            # TODO: Cambiar estado en el canal

        elif args == 'off':
            if user not in members:
                bot.sendMessage(chatID, 'No sabía que estabas en DAFI ⚠️')
                return
            r.remove_member(user)
            update.effective_message.reply_text(
                'He anotado que has salido de DAFI ✅')
            # TODO: Cambiar estado en el canal

    elif members:
        text = 'Hay alguien en DAFI, ¿quieres que avise de que vas? ✅'
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Estoy de camino 🏃🏻‍♂️", callback_data='dafi-omw-{}'.format(telegramUser.id))],
            [InlineKeyboardButton("Iré luego ☕️", callback_data='dafi-later-{}'.format(telegramUser.id))]
        ])
        bot.sendMessage(chatID, text, reply_markup=keyboard)

    else:
        bot.sendMessage(chatID, 'Ahora mismo no hay nadie en DAFI 😓')


def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('dafi', dafi_room))
    dispatcher.add_handler(CallbackQueryHandler(dafi_callback, pattern='dafi'))
