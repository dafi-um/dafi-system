from enum import Enum

from telegram import (
    ParseMode,
    TelegramError,
    Update,
)
from telegram.ext import CallbackContext
from telegram.replymarkup import ReplyMarkup

from bot.decorators import auto_answer_query
from main.models import Config
from users.models import User

from ..utils import (
    create_reply_markup,
    create_users_list,
    prepare_callback,
)


class RoomActions(str, Enum):

    ON = 'on'
    OFF = 'off'


def _cmd_no_options(update: Update, members: list[User]) -> None:
    assert update.effective_chat is not None
    assert update.effective_message is not None

    if not members:
        assert update.effective_user

        update.effective_message.reply_text(
            'Ahora mismo no hay nadie en DAFI 😓',

            reply_markup=create_reply_markup(
                [(
                    'Avísame cuando llegue alguien ✔️',
                    'dafi:notify:{}'.format(update.effective_user.id)
                )],
                [('No me avises ❌', 'main:okey')]
            )
        )

        return

    msg = '🏠 *DAFI* 🎓\nEn la delegación está{}...\n\n{}'.format(
        'n' if len(members) > 1 else '',
        create_users_list(members)
    )

    reply_markup: 'ReplyMarkup | None' = None

    if update.effective_chat.type == 'private':
        msg += '\n\n¿Quieres que avise de que vas?'

        reply_markup = create_reply_markup(
            [('Sí, estoy de camino 🏃🏻‍♂️', 'dafi:omw')],
            [('No, iré luego ☕️', 'dafi:cancel')],
        )

    update.effective_message.reply_markdown(
        msg,
        reply_markup=reply_markup
    )


def cmd_dafi(update: Update, context: CallbackContext[dict, dict, dict]) -> None:
    assert update.effective_message is not None
    assert update.effective_user is not None

    members_ids: list[str] = []

    try:
        members_ids = context.bot_data['room_members']
    except KeyError:
        context.bot_data['room_members'] = members_ids

    members = list(User.objects.filter(telegram_id__in=members_ids))

    if not context.args:
        _cmd_no_options(update, members)
        return

    try:
        user = User.objects.filter(telegram_id=update.effective_user.id).get()
        assert user.has_perm('bot.can_change_room_state')
    except (User.DoesNotExist, AssertionError):
        update.effective_message.reply_text(
            'No tienes permiso para ejecutar esta acción ❌'
        )
        return

    try:
        action = RoomActions(context.args[0])
    except ValueError:
        update.effective_message.reply_markdown(
            'Uso: `/dafi <on|off|lista>`'
        )
        return

    queue: list[str] = []

    try:
        queue = context.bot_data['room_queue']
    except KeyError:
        context.bot_data['room_queue'] = queue

    if action == RoomActions.ON:
        if user.telegram_id in members:
            update.effective_message.reply_text(
                'Ya tenía constancia de que estás en DAFI ⚠️'
            )
            return

        members_ids.append(update.effective_user.id)

        msg = f'@{user.telegram_user} acaba de llegar a DAFI 🔔'

        if len(queue):
            for user_id in queue:
                try:
                    context.bot.send_message(user_id, msg)
                except TelegramError:
                    # So many errors can occur here but it's a simple
                    # notification, so we'll just ignore a failed one
                    pass

            queue.clear()

        update.effective_message.reply_text(
            'He anotado que estás en DAFI ✅',

            reply_markup=create_reply_markup([
                ('Me voy 💤', 'dafi:off'),
            ]),
        )
    elif action == RoomActions.OFF:
        if user not in members:
            update.effective_message.reply_text(
                'No sabía que estabas en DAFI ⚠️'
            )
            return

        members_ids.remove(update.effective_user.id)

        update.effective_message.reply_text(
            'He anotado que has salido de DAFI ✅'
        )


@auto_answer_query
def callback_dafi(update: Update, context: CallbackContext[dict, dict, dict]) -> None:
    assert update.effective_message is not None
    assert update.effective_user is not None

    queue: list[str] = []

    try:
        queue = context.bot_data['room_queue']
    except KeyError:
        context.bot_data['room_queue'] = queue

    query, action, _ = prepare_callback(update)

    if action == 'notify':
        user_id = update.effective_user.id

        query.edit_message_reply_markup() # To remove the button

        if user_id not in queue:
            queue.append(user_id)

        update.effective_message.reply_text(
            'Hecho, te avisaré 😉'
        )
        return
    elif action == 'cancel':
        query.edit_message_reply_markup() # To remove the button

        update.effective_message.reply_text(
            '¡De acuerdo!'
        )
        return

    members_ids: list[str] = []

    try:
        members_ids = context.bot_data['room_members']
    except KeyError:
        context.bot_data['room_members'] = members_ids

    members = list(User.objects.filter(telegram_id__in=members_ids))

    if action == 'omw':
        if not members:
            query.edit_message_text(
                'Ahora mismo no hay nadie en DAFI 😓'
            )
            return

        group_id = Config.get(Config.MAIN_GROUP_ID)

        try:
            assert group_id is not None

            context.bot.send_message(
                group_id,
                f'¡{update.effective_user.name} está de camino a DAFI!',
            )
        except (TelegramError, AssertionError):
            update.effective_message.reply_text(
                'No he podido avisarles 😓'
            )
            return

        query.edit_message_reply_markup() # To remove the button

        update.effective_message.reply_text(
            'Hecho, les he avisado 😉'
        )
        return

    try:
        user = User.objects.filter(telegram_id=update.effective_user.id).get()
        assert user.has_perm('bot.can_change_room_state')
    except (User.DoesNotExist, AssertionError):
        query.edit_message_text(
            'No tienes permiso para ejecutar esta acción ❌'
        )
        return

    if action == 'off':
        if user not in members:
            query.edit_message_text(
                'No sabía que estabas en DAFI ⚠️'
            )
            return

        members_ids.remove(update.effective_user.id)

        query.edit_message_text(
            'He anotado que has salido de DAFI ✅'
        )


def job_dafi(context: CallbackContext[dict, dict, dict]) -> None:
    members_ids: list[str] = context.bot_data.get('room_members', [])

    msg = (
        '¡Oye! Parece que te has dejado activado el `/dafi` y la '
        'facultad ya ha cerrado. Quizás deberías ejecutar `/dafi off` '
        '(o pulsar este botón).'
    )

    reply_markup = create_reply_markup([
        ('Salir de DAFI 💤', 'dafi:off'),
    ])

    for member_id in members_ids:
        context.bot.send_message(
            member_id,
            msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )
