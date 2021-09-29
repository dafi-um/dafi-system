from django.db.models import Q

from telegram import (
    Message,
    Update,
)
from telegram.ext import CallbackContext

from heart.models import Group

from ..decorators import limit_chat_type


@limit_chat_type('group')
def cmd_mention(update: Update, context: CallbackContext) -> None:
    assert context.args is not None
    assert update.effective_chat is not None
    assert update.effective_message is not None

    query = Q()

    if context.args:
        try:
            for pair in context.args:
                nums = [int(x) for x in pair.split('.')]

                subquery = Q(year__year=nums[0], year__degree_id='GII')

                if len(nums) > 1:
                    subquery &= Q(number=nums[1])

                query |= subquery
        except ValueError:
            update.effective_message.reply_markdown(
                'Uso: `/mencionar <año>[.<grupo>] [<año>[.<grupo>]]`\n'
                'Ejemplo: `/mencionar 3.1` para los delegados del grupo 1 de tercero\n'
                'Ejemplo: `/mencionar 2 3` para todos los delegados de segundo y tercero'
            )
            return

    groups = (
        Group
        .objects
        .filter(query & ~Q(delegate=None, subdelegate=None))
        .prefetch_related('delegate', 'subdelegate')
    )

    if not groups:
        update.effective_message.reply_markdown(
            'No se han encontrado delegados para mencionar 😓'
        )
        return

    msg = ''

    for group in groups:
        if group.delegate:
            msg += ' @' + group.delegate.telegram_user

        if group.subdelegate:
            msg += ' @' + group.subdelegate.telegram_user

    if isinstance(update.effective_message.reply_to_message, Message):
        update.effective_message.reply_to_message.reply_text(msg)
    else:
        update.effective_chat.send_message(msg)
