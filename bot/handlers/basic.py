from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.ext import CommandHandler

def start(update, context):
    update.message.reply_text("Hola {}, soy el DAFI Bot. ¿En qué puedo ayudarte?".format(update.message.from_user.first_name))

def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized as e:
        print(e)
    except BadRequest as e:
        print(e)
    except TimedOut as e:
        print(e)
    except NetworkError as e:
        print(e)
    except ChatMigrated as e:
        print(e)
    except TelegramError as e:
        print(e)

def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_error_handler(error_callback)
