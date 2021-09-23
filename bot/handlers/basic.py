from telegram import (
    Message,
    TelegramError,
    Update,
)
from telegram.ext import CallbackContext

from users.models import User

from ..utils import create_reply_markup
from .handlers import (
    BasicBotHandler,
    add_handlers,
)


@add_handlers
class MainHandler(BasicBotHandler):
    """Start command and generic callback handler.
    """

    cmd = 'start'
    query_prefix = 'main'

    def command(self, update: Update, context: CallbackContext):
        assert update.effective_chat is not None
        assert isinstance(update.message, Message)

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

            reply_markup = create_reply_markup([
                ('Sí, vincular cuenta', 'users:link'),
                ('No, cancelar', 'main:abort'),
            ])

            return msg, reply_markup

    def callback(self, update: Update, context: CallbackContext, action, *args):
        if action == 'abort':
            return 'Operación cancelada.'
        elif action == 'okey':
            return '¡De acuerdo!'


@add_handlers
class GetGroupID(BasicBotHandler):
    """Sends the user a chat ID keeping it secret (only superusers)"""

    cmd = 'getid'

    def command(self, update: Update, context: CallbackContext):
        user: 'User | None' = self.get_user()

        if not user or not user.is_superuser:
            return

        chat = update.effective_chat
        assert chat is not None

        msg = 'ID de {}: {}'.format(
            chat.title or chat.username or 'desconocido', chat.id
        )

        assert update.effective_message is not None

        try:
            update.effective_message.delete()
        except TelegramError:
            msg += '\n(No he podido eliminar el comando del chat)'

        self.answer_private(msg)
