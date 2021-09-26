import logging
from functools import partial

from telegram import (
    ParseMode,
    Update,
)
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from heart.models import Group
from main.models import Config
from users.models import User

from ...decorators import auth_required
from ...utils import create_reply_markup


logger = logging.getLogger(__name__)


def basecmd_im_delegate(
        is_delegate: bool,
        update: Update,
        context: CallbackContext[dict, dict, dict],
        user: User) -> None:
    assert context.args is not None
    assert update.effective_message is not None
    assert update.effective_user is not None
    assert isinstance(update.effective_user.username, str)

    if not context.bot_data.get('elections', False):
        update.effective_message.reply_text(
            'No hay un periodo de elecciones activo ⚠️'
        )
        return

    prefix = '' if is_delegate else 'sub'

    try:
        group_id = int(context.args[0])
    except (ValueError, IndexError):
        update.effective_message.reply_markdown(
            '**Uso**: _/soy{0}delegado <ID>_\n\n'.format(prefix)
        )
        return

    try:
        group = Group.objects.filter(id=group_id).get()
    except Group.DoesNotExist:
        update.effective_message.reply_text(
            'El grupo especificado no existe ❌'
        )
        return

    msg = (
        '*Petición para ser {}delegado*\n\n'
        'Grupo: {}\nNombre: {}\nEmail: {}\nTelegram: @{}'
    ).format(
        prefix, group, user.get_full_name(), user.email,
        update.effective_user.username.replace('_', '\\_')
    )

    current = group.delegate if is_delegate else group.subdelegate

    if current:
        msg += '\n\nActual {}delegado: {}'.format(prefix, current.get_full_name())

    query = '{}:{}:{}'.format(
        user.id, group.id, int(is_delegate)
    )

    reply_markup = create_reply_markup([
        ('Autorizar ✅', 'elections_request:accept:' + query),
        ('Denegar ❌', 'elections_request:deny:' + query),
    ])

    group_id = Config.get(Config.MAIN_GROUP_ID)

    try:
        assert group_id is not None

        context.bot.send_message(
            group_id,
            msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except (TelegramError, AssertionError):
        logger.exception('Could not send an elections request message')

        update.effective_message.reply_text(
            'No se ha podido enviar tu solicitud ⚠️'
        )
        return

    update.effective_message.reply_text(
        '¡Tu solicitud se ha enviado correctamente! 🎉'
    )


cmd_im_delegate = auth_required()(partial(basecmd_im_delegate, True))
cmd_im_subdelegate = auth_required()(partial(basecmd_im_delegate, False))
