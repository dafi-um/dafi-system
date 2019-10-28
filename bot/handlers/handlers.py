from telegram import ParseMode as _ParseMode
from telegram.error import BadRequest, ChatMigrated

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
    bot_admin_required_msg = 'El bot debe ser administrador para vincular el grupo.'

    user_required = False
    user_required_msg = (
        'Debes vincular tu cuenta de usuario primero: '
        'ejecuta /vincular en un chat privado conmigo.'
    )
    user_denied_msg = 'No tienes los permisos necesarios para realizar esta acción.'

    keep_original_message = True

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

    def get_invite_link(self):
        chat_id = self.update.effective_chat.id
        chat = self.context.bot.get_chat(chat_id)

        if chat.invite_link:
            return chat_id, chat.invite_link

        try:
            return chat_id, self.context.bot.export_chat_invite_link(chat_id)
        except BadRequest:
            return None, None
        except ChatMigrated as e:
            chat_id = e.new_chat_id

        try:
            return chat_id, self.context.bot.export_chat_invite_link(chat_id)
        except BadRequest:
            return None, None

    def run_checks(self):
        chat = self.update.effective_chat

        if self.chat_type and self.chat_type not in chat.type:
            self.msg = 'Este comando solamente puede utilizarse en {} ⚠️'.format(
                self.chat_type_messages[self.chat_type]
            )
            return False

        if self.bot_admin_required and 'group' in chat.type:
            bot_id = self.context.bot.get_me().id

            if chat.get_member(bot_id).status != 'administrator':
                self.msg = self.bot_admin_required_msg
                return False

        if self.user_required:
            user = self.get_user()
            error = None

            if not user:
                error = self.user_required_msg
            elif not self.user_filter(user):
                error = self.user_denied_msg

            if error:
                self.keep_original_message = True
                self.msg = error
                return False

        return True

    def answer_as_reply(self):
        self.keep_original_message = True

    def answer_private(self, msg, reply_markup=None):
        raise NotImplementedError()

    def notify_group(self, msg, reply_markup=None):
        raise NotImplementedError()

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

    keep_original_message = False

    def parse_answer(self):
        self.update.callback_query.answer()

        if not super().parse_answer():
            self.msg = 'Parece que ha ocurrido un error inesperado...'

        return True

    def send_answer(self):
        if self.keep_original_message:
            self.update.effective_message.reply_text(
                self.msg, reply_markup=self.reply_markup
            )
        else:
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
