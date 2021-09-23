from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.contrib.auth import get_user_model
from django.test import TestCase

from .utils import create_reply_markup, create_users_list

User = get_user_model()


class StubUser():
    def __init__(self, name, t_user, t_id):
        self.name = name
        self.telegram_user = t_user
        self.telegram_id = t_id

    def get_full_name(self):
        return self.name


class BotUtilitiesTests(TestCase):
    def setUp(self):
        self.u1 = StubUser('u1', 'u1', '1111')
        self.u2 = StubUser('u2', 'u2', '2222')
        self.u3 = StubUser('u3', 'u3', '3333')

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

        # Single type: url
        m1 = InlineKeyboardMarkup([[
            InlineKeyboardButton('single_data_t1', url='single_data_u1'),
            InlineKeyboardButton('single_data_t2', url='single_data_u2'),
        ]])

        m2 = create_reply_markup([
            ('single_data_t1', None, 'single_data_u1'),
            ('single_data_t2', None, 'single_data_u2'),
        ])

        self.assertDictEqual(
            m1.to_dict(), m2.to_dict(),
            'single type (url) reply_markup not working'
        )

        # Mixed type: callback_data and url
        m1 = InlineKeyboardMarkup([[
            InlineKeyboardButton('mixed_t1', callback_data='mixed_d1'),
            InlineKeyboardButton('mixed_t2', url='mixed_u1'),
            InlineKeyboardButton('mixed_t3', callback_data='mixed_d2'),
            InlineKeyboardButton('mixed_t4', url='mixed_u2'),
        ]])

        m2 = create_reply_markup([
            ('mixed_t1', 'mixed_d1'),
            ('mixed_t2', None, 'mixed_u1'),
            ('mixed_t3', 'mixed_d2'),
            ('mixed_t4', None, 'mixed_u2'),
        ])

        self.assertDictEqual(
            m1.to_dict(), m2.to_dict(),
            'mixed types reply_markup not working'
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

        # Multiple rows multiple type
        m1 = InlineKeyboardMarkup([
            [InlineKeyboardButton('multirow_mult_t1', callback_data='multirow_mult_d1')],
            [InlineKeyboardButton('multirow_mult_t2', url='multirow_mult_u1')],
            [InlineKeyboardButton('multirow_mult_t3', callback_data='multirow_mult_d2')],
            [InlineKeyboardButton('multirow_mult_t4', url='multirow_mult_u2')],
        ])

        m2 = create_reply_markup(
            [('multirow_mult_t1', 'multirow_mult_d1')],
            [('multirow_mult_t2', None, 'multirow_mult_u1')],
            [('multirow_mult_t3', 'multirow_mult_d2')],
            [('multirow_mult_t4', None, 'multirow_mult_u2')],
        )

        self.assertDictEqual(
            m1.to_dict(), m2.to_dict(),
            'multiple rows multiple type reply_markup not working'
        )

    def test_create_users_list(self):
        """Checks the returned values in create_users_list for valid inputs"""

        # No user
        users = []
        l1 = '\nNo hay usuarios para mostrar...'
        l2 = create_users_list(users)

        self.assertEqual(l1, l2, 'empty list generated string not working')

        # Single user
        users = [self.u1]
        l1 = '\n[u1](tg://user?id=1111)'
        l2 = create_users_list(users)

        self.assertEqual(l1, l2, 'single users generated string not working')

        # Multiple users
        users = [self.u1, self.u2, self.u3]
        l1 = '\n[u1](tg://user?id=1111)\n[u2](tg://user?id=2222)\n[u3](tg://user?id=3333)'
        l2 = create_users_list(users)

        self.assertEqual(l1, l2, 'multiple users generated string not working')
