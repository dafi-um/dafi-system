from telegram import ParseMode as _ParseMode

from telegram.ext import (
    CallbackQueryHandler as _CallbackQueryHandler,
    CommandHandler as _CommandHandler,
    run_async
)

from django.contrib.auth import get_user_model as _get_user_model

_user_model = _get_user_model()

_handlers = []


class BasicHandler():
    '''Basic bot handler functionality and checks'''

    chat_type = None
    chat_type_messages = {
        'private': 'chats privados',
        'group': 'grupos'
    }

    bot_admin_required = False
    bot_admin_required_msg = 'El bot debe ser administrador para vincular el grupo'

    user_required = False
    user_required_msg = (
        'Debes vincular tu cuenta de usuario primero: '
        'ejecuta /vincular en un chat privado conmigo'
    )

    def __init__(self, update, context):
        self.update = update
        self.context = context

        self.user = None
        self.user_loaded = False

        self.msg = None
        self.reply_markup = None

    def get_user(self):
        if not self.user_loaded:
            user_id = self.update.effective_user.id
            self.user = _user_model.objects.filter(telegram_id=user_id).first()
            self.user_loaded = True

        return self.user

    def user_filter(self, user):
        return True

    def run_checks(self):
        chat = self.update.effective_chat

        if self.chat_type and self.chat_type not in chat.type:
            self.msg = 'Este comando solamente puede utilizarse en {} ⚠️'.format(
                self.chat_type_messages[self.chat_type]
            )
            return False

        if self.bot_admin_required and chat.type == 'group':
            bot_id = self.context.bot.get_me().id

            if chat.get_member(bot_id).status != 'administrator':
                self.msg = self.bot_admin_required_msg
                return False

        if self.user_required:
            user = self.get_user()

            if not user or not self.user_filter(user):
                self.msg = self.user_required_msg
                return False

        return True

    def handle(self, update, context):
        raise NotImplementedError("Must create a `handle' method in the class")

    def parse_answer(self):
        answer = self.handle(self.update, self.context)

        if not answer:
            return False

        if isinstance(answer, str):
            self.msg = answer
        elif isinstance(answer, tuple) and len(answer) == 2:
            self.msg, self.reply_markup = answer

        return True

    def send_answer(self):
        pass

    @run_async
    def run(self):
        if self.run_checks() and not self.parse_answer():
            return

        if self.msg:
            self.send_answer()

    @classmethod
    def as_handler(cls, cmd):
        def handler(update, context):
            return cls(update, context).run()

        return handler


class CommandHandler(BasicHandler):
    '''Bot command handler'''

    def send_answer(self):
        self.update.effective_message.reply_text(
            self.msg, reply_markup=self.reply_markup,
            parse_mode=_ParseMode.MARKDOWN
        )

    @classmethod
    def as_handler(cls, cmd):
        return _CommandHandler(cmd, super().as_handler(cmd))


class QueryHandler(BasicHandler):
    '''Bot callback query handler'''

    def _get_user_id(self):
        return self.update.callback_query.from_user.id

    def parse_answer(self):
        self.update.callback_query.answer()

        if not super().parse_answer():
            self.msg = 'Parece que ha ocurrido un error inesperado...'

        return True

    def send_answer(self):
        self.update.callback_query.edit_message_text(
            self.msg, reply_markup=self.reply_markup
        )

    @classmethod
    def as_handler(cls, pattern):
        return _CallbackQueryHandler(super().as_handler(pattern), pattern=pattern)


def add_handler(cmd):
    def decorator(cls):
        handler = cls.as_handler(cmd)

        _handlers.append(handler)

        return handler

    return decorator

def get_handlers():
    return _handlers
