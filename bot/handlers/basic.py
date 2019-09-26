from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model

from .handlers import CommandHandler, QueryHandler, add_handler

User = get_user_model()


@add_handler('start')
class StartHandler(CommandHandler):
    '''Start command'''

    def handle(self, update, context):
        if update.effective_chat.type != 'private':
            return

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
    '''Sends the user a chat ID keeping it secret (only superusers)'''

    def handle(self, update, context):
        user = self.get_user()

        if not user or not user.is_superuser:
            return

        chat = update.effective_chat

        msg = 'ID de {}: {}'.format(
            chat.title or chat.username or 'desconocido', chat.id
        )

        try:
            update.effective_message.delete()
        except:
            msg += '\n(No he podido eliminar el comando del chat)'

        self.context.bot.send_message(update.effective_user.id, msg)
