from typing import (
    Callable,
    cast,
)

from telegram import (
    CallbackQuery,
    ParseMode,
    Update,
)
from telegram.ext import CallbackContext

from users.models import User


BOT_ADMIN_REQUIRED = (
    'El bot debe ser administrador para realizar esta acción ⚠️'
)

USER_REQUIRED_ERROR = (
    'Debes vincular tu cuenta de usuario primero: '
    'ejecuta /vincular en un chat privado conmigo.'
)

PERMISSION_DENIED_ERROR = (
    'No tienes los permisos necesarios para realizar esta acción ❌'
)

INVALID_CHAT_TYPE = (
    'Este comando solamente puede ejecutarse en {} ⚠️'
)

CHAT_TYPES = {
    'private': 'chats privados',
    'group': 'grupos'
}


def auth_required(
        *perms: str,
        auth_error_msg: str = None,
        perm_error_msg: str = None,
        only_superuser: bool = False,
        silent: bool = False):
    """Authentication required decorator factory.

    Checks that the handler is invoked by an user registered in the web
    app. If it's not, sends an error message without executing the
    decorated handler.

    If given a list of permissions, verifies that the user has all of
    them or sends an error message.
    """
    def decorator(func: Callable[[Update, CallbackContext, User], None]):
        def decorated_func(update: Update, context: CallbackContext) -> None:
            assert update.effective_user is not None
            assert update.effective_message is not None

            user_id = update.effective_user.id

            try:
                user = User.objects.filter(telegram_id=user_id).get()
            except User.DoesNotExist:
                if not silent:
                    update.effective_message.reply_text(
                        auth_error_msg or USER_REQUIRED_ERROR,
                        parse_mode=ParseMode.MARKDOWN
                    )
                return

            if only_superuser and not user.is_superuser or (perms and not user.has_perms(perms)):
                if not silent:
                    update.effective_message.reply_text(
                        perm_error_msg or USER_REQUIRED_ERROR,
                        parse_mode=ParseMode.MARKDOWN
                    )
                return

            func(update, context, user)

        return decorated_func

    return decorator


def bot_admin_required(silent: bool = False):
    """Bot admin required decorator factory.

    Ensures that the bot has administrator permissions in the (group)
    chat that the handler is receiving.

    On error, if not silent, answers with the allowed chat types.
    """
    def decorator(func: Callable[[Update, CallbackContext], None]):
        def decorated_func(update: Update, context: CallbackContext) -> None:
            assert update.effective_chat is not None
            assert update.effective_message is not None

            bot_id = context.bot.get_me().id

            if update.effective_chat.get_member(bot_id).status != 'administrator':
                if not silent:
                    update.effective_message.reply_text(
                        BOT_ADMIN_REQUIRED,
                        parse_mode=ParseMode.MARKDOWN
                    )
                return

            func(update, context)

        return decorated_func

    return decorator


def limit_chat_type(chat_type: str, silent: bool = False):
    """Limit chat type decorator factory.

    Limits the decorated handler to certain chat types.

    On error, if not silent, answers with the allowed chat types.
    """
    def decorator(func: Callable[[Update, CallbackContext], None]):
        def decorated_func(update: Update, context: CallbackContext) -> None:
            assert update.effective_chat is not None
            assert update.effective_message is not None

            if chat_type not in update.effective_chat.type:
                if not silent:
                    update.effective_message.reply_text(
                        INVALID_CHAT_TYPE.format(CHAT_TYPES[chat_type]),
                        parse_mode=ParseMode.MARKDOWN
                    )
                return

            func(update, context)

        return decorated_func

    return decorator


def auto_answer_query(func: Callable[[Update, CallbackContext], None]):
    """Automatically answer query decorator.

    Answers the callback query, if found, when the decorated function
    has finished execution.
    """
    def decorated_func(update: Update, context: CallbackContext) -> None:
        func(update, context)

        if update.callback_query is not None:
            cast(CallbackQuery, update.callback_query).answer()

    return decorated_func
