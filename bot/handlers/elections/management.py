from telegram import Update
from telegram.ext import CallbackContext

from heart.models import Group
from users.models import User

from ...decorators import (
    auth_required,
    auto_answer_query,
)
from ...utils import (
    create_reply_markup,
    prepare_callback,
)


@auth_required('bot.can_manage_elections', silent=True)
def cmd_toggle_elections(update: Update, context: CallbackContext, user: User) -> None:
    assert update.effective_message is not None

    msg = 'El periodo de elecciones está '

    if context.bot_data.get('elections', False):
        msg += '*activo*. ¿Quieres finalizarlo?'
        btn = ('Sí, finalizar 🔒', 'elections_toggle:off')
    else:
        msg += '*inactivo*. ¿Quieres iniciarlo?'
        btn = ('Sí, iniciar ✅', 'elections_toggle:on')

    update.effective_message.reply_markdown(
        msg,
        reply_markup=create_reply_markup([
            btn,
            ('No, cancelar ❌', 'main:abort'),
        ]),
    )


@auto_answer_query
def callback_toggle_elections(update: Update, context: CallbackContext) -> None:
    assert update.effective_message is not None
    assert update.effective_user is not None

    query, action, _ = prepare_callback(update)

    if action == 'on':
        if context.bot_data.get('elections', False):
            query.edit_message_text(
                '¡El periodo de elecciones ya está activo! ⚠️'
            )
            return

        context.bot_data['elections'] = True

        query.edit_message_text(
            'Ahora el periodo de elecciones está activo ✅'
        )
    elif action == 'off':
        if not context.bot_data.get('elections', False):
            query.edit_message_text(
                '¡El periodo de elecciones ya está inactivo! ⚠️'
            )
            return

        context.bot_data['elections'] = False

        query.edit_message_text(
            'Ahora el periodo de elecciones está inactivo 🔒'
        )


@auto_answer_query
@auth_required('bot.can_manage_elections', silent=True)
def callback_delegate_request(update: Update, context: CallbackContext, user: User) -> None:
    assert update.effective_message is not None

    query, action, args = prepare_callback(update)

    try:
        requester_id = int(args[0])
        group_id = int(args[1])
        is_delegate = bool(int(args[2]))
    except (IndexError, ValueError):
        query.edit_message_text(
            'Formato de petición incorrecto ⚠️'
        )
        return

    try:
        requester = User.objects.filter(id=requester_id).get()
        group = Group.objects.filter(id=group_id).get()
    except User.DoesNotExist:
        update.effective_message.reply_text(
            '¡No se ha podido encontrar el usuario! ⚠️'
        )
        return
    except Group.DoesNotExist:
        update.effective_message.reply_text(
            'El grupo indicado no existe ⚠️'
        )
        return

    accepted = action == 'accept'
    prefix = '' if is_delegate else 'sub'

    if action == 'accept':
        Group.objects.filter(delegate=requester).update(delegate=None)
        Group.objects.filter(subdelegate=requester).update(subdelegate=None)

        if is_delegate:
            group.delegate = requester
        else:
            group.subdelegate = requester

        group.save(update_fields=(prefix + 'delegate',))

    if accepted:
        requester_answer = (
            'Tu petición ha sido aceptada, ahora eres {}delegado del {} 🎓'
        ).format(prefix, group)
    else:
        requester_answer = 'Tu petición para ser {}delegado ha sido denegada ❌'.format(prefix)

    context.bot.send_message(requester.telegram_id, requester_answer)

    msg = 'La solicitud de {} (@{}) ha sido {} por {}'.format(
        requester.get_full_name(),
        requester.telegram_user,
        'aceptada' if accepted else 'denegada',
        user.get_full_name()
    )

    if accepted:
        msg += ' ✅\n\nAhora {} es {}delegado del {}'.format(
            requester.get_full_name(), prefix, group
        )
    else:
        msg += ' ❌'

    query.edit_message_text(msg)
