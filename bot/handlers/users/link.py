from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyMarkup,
    Update,
)
from telegram.ext import CallbackContext

from main.utils import get_url
from users.models import User

from ...decorators import (
    auth_required,
    auto_answer_query,
    limit_chat_type,
)
from ...utils import create_reply_markup


@limit_chat_type('private')
def cmd_link(update: Update, context: CallbackContext) -> None:
    assert update.effective_message is not None
    assert update.effective_user is not None

    telegram_user = update.effective_user
    user = User.objects.filter(telegram_user__iexact=telegram_user.username).first()

    msg: str
    reply_markup: 'ReplyMarkup | None' = None

    if user and not user.telegram_id:
        msg = (
            f'He encontrado una cuenta con el email {user.email}, '
            '¿quieres vincular esta cuenta con tu usuario de Telegram?'
        )

        reply_markup = create_reply_markup([
            ('Vincular cuenta', 'users:link'),
            ('Cancelar', 'main:abort'),
        ])
    elif not user:
        msg = (
            'No he encontrado ninguna cuenta para vincular, '
            'recuerda introducir tu usuario de telegram en el '
            'apartado Mi Perfil de la web.'
        )

        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('Mi Perfil', url=get_url('profile')),
        ]])
    else:
        msg = 'Esta cuenta ya está vinculada a '

        if user.telegram_id == telegram_user.id:
            msg += 'tu usuario ✅'
        else:
            msg += 'otro usuario ⚠️'

    update.effective_message.reply_markdown(
        msg, reply_markup=reply_markup,
    )


@auto_answer_query
def callback_link(update: Update, context: CallbackContext) -> None:
    assert update.effective_message is not None
    assert update.effective_user is not None

    updated = (
        User
        .objects
        .filter(
            telegram_user__iexact=update.effective_user.username,
            telegram_id=None,
        )
        .update(telegram_id=update.effective_user.id)
    )

    if not updated:
        update.effective_message.edit_text(
            'Parece que ha ocurrido un error...'
        )
        return

    update.effective_message.edit_text(
        '¡He vinculado tu cuenta correctamente! ✅\n'
        'Ahora te informaré de las cosas importantes por aquí.'
    )


@limit_chat_type('private')
@auth_required()
def cmd_unlink(update: Update, context: CallbackContext, *args) -> None:
    assert update.effective_message is not None

    update.effective_message.reply_text(
        '⚠️ Vas a desvincular tu cuenta ⚠️\n'
        'No podrás realizar acciones importantes en DAFI desde '
        'Telegram salvo que vincules tu cuenta de nuevo.\n\n'
        '¿Estás seguro de que deseas continuar?',

        reply_markup=create_reply_markup([
            ('Sí, desvincular cuenta', 'users:unlink'),
            ('No, cancelar', 'main:abort'),
        ])
    )


@auto_answer_query
def callback_unlink(update: Update, context: CallbackContext) -> None:
    assert update.effective_message is not None
    assert update.effective_user is not None

    updated = (
        User
        .objects
        .filter(telegram_id=update.effective_user.id)
        .update(telegram_id=None)
    )

    if not updated:
        update.effective_message.edit_text(
            '¡Este usuario no está vinculado a ninguna cuenta! ❌'
        )
        return

    update.effective_message.edit_text(
        '¡He desvinculado tu cuenta correctamente! ✅'
    )
