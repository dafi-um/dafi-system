from telegram import (
    TelegramError,
    Update,
)
from telegram.ext import CallbackContext

from users.models import User

from ..decorators import (
    auth_required,
    limit_chat_type,
)
from ..utils import (
    create_reply_markup,
    prepare_callback,
)


@limit_chat_type('private', silent=True)
def cmd_start(update: Update, context: CallbackContext) -> None:
    assert update.effective_message is not None
    assert update.effective_user is not None

    update.effective_message.reply_text(
        f'Hola {update.effective_user.first_name}, soy el DAFI Bot. ¿En qué puedo ayudarte?'
    )

    user = User.objects.filter(telegram_user=update.effective_user.username).first()

    if user is None:
        return None

    if not user.telegram_id:
        update.effective_message.reply_markdown(
            f'He encontrado una cuenta de DAFI ({user.email}) '
            'con tu usuario de Telegram, ¿quieres vincularla '
            'ahora a tu cuenta de Telegram?',

            reply_markup=create_reply_markup([
                ('Sí, vincular cuenta', 'users:link'),
                ('No, cancelar', 'main:start_link_cancel'),
            ]),
        )


def callback_generic(update: Update, context: CallbackContext) -> None:
    query, action, _ = prepare_callback(update)

    if action == 'abort':
        query.edit_message_text('¡Operación cancelada!')
    elif action == 'okey':
        query.edit_message_text('¡De acuerdo!')
    elif action == 'start_link_cancel':
        query.edit_message_text(
            '¡Okey! Recuerda que puedes vincular tu cuenta en cualquier '
            'momento ejecutando /vincular'
        )

    query.answer()


@auth_required(only_superuser=True, silent=True)
def cmd_getid(update: Update, context: CallbackContext, *args) -> None:
    assert update.effective_chat is not None
    assert update.effective_message is not None
    assert update.effective_user is not None

    chat = update.effective_chat

    msg = 'ID de {}: {}'.format(
        chat.title or chat.username or 'desconocido', chat.id
    )

    try:
        update.effective_message.delete()
    except TelegramError:
        msg += '\n(No he podido eliminar el comando del chat)'

    context.bot.send_message(update.effective_user.id, msg)
