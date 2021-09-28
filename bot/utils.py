from typing import (
    Iterable,
    cast,
)

from telegram import (
    Bot,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyMarkup,
    Update,
)
from telegram.chat import Chat
from telegram.error import (
    BadRequest,
    ChatMigrated,
)

from users.models import User


def prepare_callback(update: Update) -> tuple[CallbackQuery, str, list[str]]:
    """Parses the update callback query.

    Provides a type-safe way of getting the callback query object.

    Splits the callback query data by ':', discarding the first item and
    returning the second one by itself and the remaining as a list.
    """
    assert update.callback_query is not None

    query: CallbackQuery = update.callback_query

    _, action, *args = cast(str, query.data).split(':')

    return query, action, args


def create_reply_markup(*lines: list[tuple[str, str]]) -> ReplyMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text, callback_data=data)
            for text, data in button
        ]
        for button in lines
    ])


def user_display_link(user: User) -> str:
    return '{} ([@{}](tg://user?id={}))'.format(
        user.get_full_name(), user.telegram_user, user.telegram_id
    )


def create_users_list(users: Iterable[User]) -> str:
    if not users:
        return '_No hay usuarios para mostrar_'

    return '\n'.join(user_display_link(user) for user in users)


def generate_invite_link(chat: Chat, bot: Bot) -> 'str | None':
    """Generates an invite link for the given chat.

    Returns None on error.
    """
    chat_id = chat.id

    try:
        return bot.export_chat_invite_link(chat_id)
    except BadRequest:
        return None
    except ChatMigrated as e:
        chat_id = e.new_chat_id

    try:
        return bot.export_chat_invite_link(chat_id)
    except BadRequest:
        return None
