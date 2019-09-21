from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model

from .handlers import CommandHandler, QueryHandler, add_handler

User = get_user_model()


@add_handler('start')
class StartHandler(CommandHandler):
    '''Start command'''

    def handle(self, update, context):
        telegram_user = update.message.from_user
        user = User.objects.filter(telegram_user=telegram_user.username).first()

        update.message.reply_text(
            'Hola {}, soy el DAFI Bot. ¿En qué puedo ayudarte?'.format(telegram_user.first_name)
        )

        if user and not user.telegram_id:
            msg = (
                'He encontrado una cuenta de DAFI ({}) '
                'con tu usuario de Telegram, ¿quieres vincularla '
                'ahora a tu cuenta de Telegram?'
            ).format(user.email)

            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton('Sí, vincular cuenta', callback_data='users:link'),
                InlineKeyboardButton('No, cancelar', callback_data='main:abort')
            ]])

            return msg, reply_markup


@add_handler('main')
class BasicCallbackHandler(QueryHandler):
    '''Generic callback queries handler'''

    def handle(self, update, context):
        if update.callback_query.data == 'main:abort':
            return 'Operación cancelada.'


@add_handler('getid')
class GetGroupID(CommandHandler):
    '''Prints the chat ID (only staff members)'''

    user_required = True
    user_required_msg = 'No tienes los permisos adecuados para realizar esta acción'

    def user_filter(self, user):
        return user.is_staff

    def handle(self, update, context):
        return 'ID: {}'.format(update.message.chat.id)
