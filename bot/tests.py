from django.test import TestCase

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from users.models import User

from .utils import (
    create_reply_markup,
    create_users_list,
)


class BotUtilitiesTests(TestCase):
    def setUp(self):
        self.u1 = User(first_name='u1', telegram_user='u1', telegram_id='1111')
        self.u2 = User(first_name='u2', telegram_user='u2', telegram_id='2222')
        self.u3 = User(first_name='u3', telegram_user='u3', telegram_id='3333')

    def test_create_reply_markup(self):
        """create_reply_markup returns same structures as if made manually"""

        # Single type: callback_data
        m1 = InlineKeyboardMarkup([[
            InlineKeyboardButton('single_data_t1', callback_data='single_data_d1'),
            InlineKeyboardButton('single_data_t2', callback_data='single_data_d2'),
        ]])

        m2 = create_reply_markup([
            ('single_data_t1', 'single_data_d1'),
            ('single_data_t2', 'single_data_d2'),
        ])

        self.assertDictEqual(
            m1.to_dict(), m2.to_dict(),
            'single type (callback_data) reply_markup not working'
        )

        # Multiple rows single type
        m1 = InlineKeyboardMarkup([
            [InlineKeyboardButton('multirow_single_t1', callback_data='multirow_single_d1')],
            [InlineKeyboardButton('multirow_single_t2', callback_data='multirow_single_d2')],
        ])

        m2 = create_reply_markup(
            [('multirow_single_t1', 'multirow_single_d1')],
            [('multirow_single_t2', 'multirow_single_d2')],
        )

        self.assertDictEqual(
            m1.to_dict(), m2.to_dict(),
            'multiple rows single type reply_markup not working'
        )

    def test_create_users_list(self):
        """Checks the returned values in create_users_list for valid inputs"""

        # No user
        users = []
        l1 = '_No hay usuarios para mostrar_'
        l2 = create_users_list(users)

        self.assertEqual(l1, l2, 'empty list generated string not working')

        # Single user
        users = [self.u1]
        l1 = 'u1 ([@u1](tg://user?id=1111))'
        l2 = create_users_list(users)

        self.assertEqual(l1, l2, 'single users generated string not working')

        # Multiple users
        users = [self.u1, self.u2, self.u3]
        l1 = 'u1 ([@u1](tg://user?id=1111))\nu2 ([@u2](tg://user?id=2222))\nu3 ([@u3](tg://user?id=3333))'
        l2 = create_users_list(users)

        self.assertEqual(l1, l2, 'multiple users generated string not working')
