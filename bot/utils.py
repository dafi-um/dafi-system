from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_reply_markup(*lines, prefix=None):
    buttons = []

    for items in lines:
        line = []

        for text, data, *extra in items:
            url = extra[0] if extra else None

            if prefix:
                data = prefix + ':' + data

            line.append(
                InlineKeyboardButton(text, callback_data=data, url=url)
            )

        buttons.append(line)

    return InlineKeyboardMarkup(buttons)

def create_users_list(users):
    if not users:
        return '\nNo hay usuarios para mostrar...'

    msg = ''

    for user in users:
        msg += '\n[{}](tg://user?id={})'.format(
            user.get_full_name(), user.telegram_id
        )

    return msg
