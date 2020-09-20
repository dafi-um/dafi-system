from telegram import ParseMode as _ParseMode
from telegram.error import BadRequest, ChatMigrated
from telegram.ext import CallbackQueryHandler, CommandHandler, run_async

from django.contrib.auth import get_user_model as _get_user_model

from main.models import Config

_user_model = _get_user_model()

_handlers = []


class BasicBotHandler():
    '''Basic bot handler functionality and checks'''

    cmd = None
    commands_available = []
    query_prefix = None

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

    keep_original_message = False

    disable_web_page_preview = None

    def __init__(self, update, context, cmd=None):
        self.update = update
        self.context = context

        self.is_callback = not cmd
        self.current_command = cmd

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

    def get_bot_link(self):
        return 'tg://user?id={}'.format(self.context.bot.get_me().id)

    def user_filter(self, user):
        return True

    def callback_user_filter(self, user):
        return True

    def get_invite_link(self):
        chat_id = self.update.effective_chat.id
        chat = self.context.bot.get_chat(chat_id)

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

    def is_group(self):
        return 'group' in self.update.effective_chat.type

    def run_checks(self):
        chat = self.update.effective_chat

        if self.chat_type and self.chat_type not in chat.type:
            self.msg = 'Este comando solamente puede utilizarse en {} ⚠️'.format(
                self.chat_type_messages[self.chat_type]
            )
            return False

        if self.bot_admin_required and self.is_group():
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
            elif self.is_callback and not self.callback_user_filter(user):
                error = self.user_denied_msg

            if error:
                self.keep_original_message = True
                self.msg = error
                return False

        return True

    def answer_as_reply(self):
        self.keep_original_message = True

    def answer_private(self, msg, reply_markup=None):
        return self.context.bot.send_message(
            self.update.effective_user.id, msg,
            reply_markup=reply_markup,
            parse_mode=_ParseMode.MARKDOWN,
            disable_web_page_preview=self.disable_web_page_preview
        )

    def notify_group(self, msg, reply_markup=None, parse_mode=None, config_key=None):
        if not config_key:
            config_key = Config.MAIN_GROUP_ID

        group_id = Config.get(config_key)

        if not group_id:
            return False

        self.context.bot.send_message(
            group_id, msg, parse_mode, reply_markup=reply_markup,
            disable_web_page_preview=self.disable_web_page_preview
        )

        return True

    def command(self, update, context):
        raise NotImplementedError("Must create a `command' method in the class")

    def callback(self, update, context, action, *args):
        raise NotImplementedError("Must create a `callback' method in the class")

    def send_answer(self):
        if not self.is_callback or self.keep_original_message:
            self.update.effective_message.reply_text(
                self.msg, reply_markup=self.reply_markup,
                parse_mode=_ParseMode.MARKDOWN,
                disable_web_page_preview=self.disable_web_page_preview
            )
        else:
            self.update.callback_query.edit_message_text(
                self.msg, reply_markup=self.reply_markup
            )

    @run_async
    def run(self):
        if not self.run_checks():
            return self.send_answer()

        if self.is_callback:
            query = self.update.callback_query
            query.answer()

            prefix, action, *args = query.data.split(':')

            if prefix != self.query_prefix:
                return

            answer = self.callback(self.update, self.context, action, *args)

            if not answer:
                answer = 'Parece que ha ocurrido un error inesperado...'
        else:
            answer = self.command(self.update, self.context)

            if not answer:
                return

        if isinstance(answer, str):
            self.msg = answer
        elif isinstance(answer, tuple) and len(answer) == 2:
            self.msg, self.reply_markup = answer

        self.send_answer()

    @classmethod
    def get_handlers(cls):
        handlers = []
        commands = []

        if cls.cmd:
            commands.append(cls.cmd)

        if cls.commands_available:
            commands += cls.commands_available

        if commands and callable(getattr(cls, 'command', None)):
            for cmd in commands:
                handlers.append(create_cmd_handler(cls, cmd))

        if cls.query_prefix and callable(getattr(cls, 'callback', None)):
            def callback_handler(update, context):
                return cls(update, context).run()

            handlers.append(
                CallbackQueryHandler(callback_handler, pattern=cls.query_prefix)
            )

        if len(handlers) == 0:
            raise NotImplementedError('Must implement at least one handler method!')

        return handlers


def create_cmd_handler(cls, cmd):
    def cmd_handler(update, context):
        return cls(update, context, cmd).run()

    return CommandHandler(cmd, cmd_handler)

def add_handlers(cls):
    global _handlers

    _handlers += cls.get_handlers()
    return cls

def get_handlers():
    return _handlers
