import telegram

from telegram.ext import CallbackQueryHandler, CommandHandler

_handlers = []

def add_handler(cmd):
    def decorator(function):
        def wrapper(update, context):
            answer = function(update, context)

            if not answer:
                return

            msg = reply_markup = None

            if isinstance(answer, str):
                msg = answer
            elif isinstance(answer, tuple) and len(answer) == 2:
                msg, reply_markup = answer

            if msg:
                update.message.reply_text(
                    msg, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN
                )

        _handlers.append(CommandHandler(cmd, wrapper))

        return wrapper

    return decorator

def add_query_handler(pattern):
    def decorator(function):
        def wrapper(update, context):
            update.callback_query.answer()

            answer = function(update, context)

            msg = reply_markup = None

            if not answer:
                msg = 'Parece que ha ocurrido un error inesperado...'
            elif isinstance(answer, str):
                msg = answer
            elif isinstance(answer, tuple) and len(answer) == 2:
                msg, reply_markup = answer

            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)

        _handlers.append(CallbackQueryHandler(wrapper, pattern=pattern))

        return wrapper

    return decorator

def get_handlers():
    return _handlers
