from datetime import timedelta

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.shortcuts import reverse
from django.template import Context, Template
from django.test import Client, TestCase
from django.utils import timezone

from .models import Subject, TradeOffer, TradeOfferAnswer, TradeOfferLine, TradePeriod

User = get_user_model()


class TradingModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester', email='test@test.com', password='1234')

        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=1)
        Subject.objects.create(code=2, name='Subject 2', acronym='S2', quarter=1, year=2)

        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() + timedelta(hours=2)

        self.period = TradePeriod.objects.create(name='Period 1', start=start, end=end)

    def test_tradeofferline_getters(self):
        '''TradeOfferLine getters return correct values'''

        line = TradeOfferLine()

        line.subjects = ''
        self.assertEquals(line.get_subjects_list(), [])
        self.assertEquals(line.get_subjects().count(), 0)

        line.subjects = '1'
        self.assertEquals(line.get_subjects_list(), [1])
        self.assertEquals(line.get_subjects().count(), 1)

        line.subjects = '1,2'
        self.assertEquals(line.get_subjects_list(), [1,2])
        self.assertEquals(line.get_subjects().count(), 2)

        line.subjects = '1,a'
        self.assertEquals(line.get_subjects_list(), [])
        self.assertEquals(line.get_subjects().count(), 0)

        line.subjects = 'not_valid'
        self.assertEquals(line.get_subjects_list(), [])
        self.assertEquals(line.get_subjects().count(), 0)

    def test_tradeofferline_validate_subjects(self):
        '''TradeOfferLine validates subjects properly'''

        line = TradeOfferLine(year=1, curr_group=1, curr_subgroup=1, wanted_groups='2')

        with self.assertRaisesMessage(ValidationError, 'Valor de asignaturas inválido'):
            line.subjects = 'not_valid'
            line.full_clean(['offer'])

        with self.assertRaisesMessage(ValidationError, 'Código de asignatura incorrecto'):
            line.subjects = '3'
            line.full_clean(['offer'])

        with self.assertRaisesMessage(ValidationError, 'La asignatura 2 es de un año distinto'):
            line.subjects = '2'
            line.full_clean(['offer'])

        with self.assertRaisesMessage(ValidationError, 'La asignatura 2 es de un año distinto'):
            line.subjects = '1,2'
            line.full_clean(['offer'])

        try:
            line.subjects = '1'
            line.full_clean(['offer'])
        except ValidationError:
            self.fail('Subject is valid but validation failed')

    def test_tradeofferline_validate_groups(self):
        '''TradeOfferLine validates groups properly'''

        line = TradeOfferLine(year=1, curr_group=1, curr_subgroup=1, subjects='1')

        with self.assertRaisesMessage(ValidationError, 'Valor de grupos buscados inválido'):
            line.wanted_groups = 'not_valid'
            line.full_clean(['offer'])

        with self.assertRaisesMessage(ValidationError, 'El grupo 5 no existe en Año 1'):
            line.wanted_groups = '5'
            line.full_clean(['offer'])

        with self.assertRaisesMessage(ValidationError, 'El grupo 5 no existe en Año 1'):
            line.wanted_groups = '2,5'
            line.full_clean(['offer'])

        self.assertEquals(line.get_wanted_groups(), [2, 5], 'Comma separated list not parsed properly')

        with self.assertRaisesMessage(ValidationError, 'El grupo actual no puede estar en los grupos buscados'):
            line.wanted_groups = '1'
            line.full_clean(['offer'])

        try:
            line.wanted_groups = '2'
            line.full_clean(['offer'])
        except ValidationError:
            self.fail('Wanted groups is valid but validation failed')

        with self.assertRaisesMessage(ValidationError, 'El grupo 5 no existe en Año 1'):
            line.curr_group = '5'
            line.full_clean(['offer'])

        try:
            line.curr_group = '1'
            line.full_clean(['offer'])
        except ValidationError:
            self.fail('Current group is valid but validation failed')

        with self.assertRaisesMessage(ValidationError, 'El subgrupo 1.5 no existe en Año 1'):
            line.curr_subgroup = '5'
            line.full_clean(['offer'])

        try:
            line.curr_subgroup = '1'
            line.full_clean(['offer'])
        except ValidationError:
            self.fail('Current subgroup is valid but validation failed')

    def test_tradeofferanswer_getter_setter_groups(self):
        '''TradeOfferAnswer groups getter and setter works properly'''

        answer = TradeOfferAnswer()

        for case in [{}, {1: [2, 1]}, {1: [2, 1], 2: [2, 1]}]:
            answer.set_groups(case)
            self.assertEquals(answer.get_groups(), case, 'getter does not returns correct output')

        answer.set_groups({})
        self.assertEquals(answer.groups, '', 'setter does not sets empty field for falsy objects')

    def test_tradeofferanswer_validate_groups(self):
        '''TradeOfferAnswer validates groups properly'''

        offer = TradeOffer.objects.create(user=self.user, period=self.period)

        TradeOfferLine.objects.create(offer=offer, year=1, curr_group='1', curr_subgroup='1', wanted_groups='2', subjects='1')
        TradeOfferLine.objects.create(offer=offer, year=2, curr_group='1', curr_subgroup='1', wanted_groups='2,3', subjects='2')

        answer = TradeOfferAnswer(offer=offer)

        for case in [{'1': [2, 1], '2': [2, 1]}, {'1': [2, 2], '2': [3, 3]}]:
            answer.set_groups(case)

            try:
                answer.full_clean(['user'])
            except ValidationError:
                self.fail('validation failed for valid data')

        cases = [
            ({}, 'Este campo no puede estar vacío.'),
            ({1: 2}, 'No hay un valor para Año 1'),
            ({'1': 2}, 'Formato incorrecto para Año 1'),
            ({'1': [2, 1]}, 'No hay un valor para Año 2'),
            ({'1': [2, 1], 2: [2, 1]}, 'No hay un valor para Año 2'),
            ({'2': [2, 1]}, 'No hay un valor para Año 1'),
            ({'2': [2, 1], 2: [2, 1]}, 'No hay un valor para Año 1'),
            ({'1': 2, '2': [2, 1]}, 'Formato incorrecto para Año 1'),
            ({'1': [2, 1], '2': [2]}, 'Formato incorrecto para Año 2'),
            ({'1': [2], '2': [2, 1]}, 'Formato incorrecto para Año 1'),
            ({'1': [2, 1], '2': 2}, 'Formato incorrecto para Año 2'),
            ({'1': [1, 1], '2': [2, 1]}, 'El grupo 1 no es un grupo buscado'),
            ({'1': [3, 1], '2': [2, 1]}, 'El grupo 3 no es un grupo buscado'),
            ({'1': [2, 1], '2': [4, 1]}, 'El grupo 4 no es un grupo buscado'),
            ({'1': [2, 0], '2': [2, 1]}, 'El subgrupo 2.0 no existe en Año 1'),
            ({'1': [2, 4], '2': [2, 1]}, 'El subgrupo 2.4 no existe en Año 1'),
            ({'1': [2, 1], '2': [2, 4]}, 'El subgrupo 2.4 no existe en Año 2'),
        ]

        for case in cases:
            with self.assertRaisesMessage(ValidationError, case[1]):
                answer.set_groups(case[0])
                answer.full_clean(['user'])


class TradingViewsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='tester_1', email='test@test.com', password='1234')
        self.user2 = User.objects.create(username='tester_2', email='test2@test.com', password='1234')
        self.user3 = User.objects.create(username='tester_3', email='test3@test.com', password='1234')
        self.user4 = User.objects.create(username='tester_4', email='test4@test.com', password='1234')
        self.user_manager = User.objects.create(username='manager', email='manager@test.com', password='1234')
        self.user_manager.user_permissions.add(Permission.objects.get(codename='is_manager'))

        self.users = [self.user1, self.user2, self.user3, self.user_manager]

        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=2)

        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() + timedelta(hours=1)
        self.period = TradePeriod.objects.create(name='Period 1', start=start, end=end)

        self.offer = TradeOffer.objects.create(user=self.user1, period=self.period)
        self.offer2 = TradeOffer.objects.create(user=self.user4, period=self.period)

        TradeOfferLine.objects.create(
            offer=self.offer, year=1, subjects='1',
            curr_group=1, curr_subgroup=1, wanted_groups='2, 3'
        )

        TradeOfferLine.objects.create(
            offer=self.offer2, year=1, subjects='1',
            curr_group=1, curr_subgroup=1, wanted_groups='2, 3'
        )

        self.answer = TradeOfferAnswer(user=self.user2, offer=self.offer)
        self.answer.set_groups({'1': [2, 1]})
        self.answer.save()

        self.answer2 = TradeOfferAnswer(user=self.user1, offer=self.offer2)
        self.answer2.set_groups({'1': [2, 1]})
        self.answer2.save()

    def period_expired(self):
        self.period.end = timezone.now() - timedelta(hours=1)
        self.period.save()

    def period_active(self):
        self.period.end = timezone.now() + timedelta(hours=1)
        self.period.save()

    def offer_accept_answer(self):
        self.offer.answer = self.answer
        self.offer.save()

    def offer_remove_answer(self):
        self.offer.answer = None
        self.offer.save()

    def test_list_view_period_access(self):
        '''TradeOffer list view restricts access properly depending on the current trading period'''

        c = Client()

        url_list = reverse('trading:list')

        self.assertNotContains(c.get(url_list), 'Periodo de Permutas no activo', msg_prefix='anonymous user cannot access list inside period')

        for user in self.users:
            c.force_login(user)
            self.assertNotContains(c.get(url_list), 'Periodo de Permutas no activo', msg_prefix='user {} cannot access list inside period'.format(user.username))
            c.logout()

        self.period_expired()

        self.assertContains(c.get(url_list), 'Periodo de Permutas no activo', msg_prefix='anonymous user can access list outside period')

        for user in [self.user1, self.user2, self.user3]:
            c.force_login(user)
            self.assertContains(c.get(url_list), 'Periodo de Permutas no activo', msg_prefix='user {} can access list outside period'.format(user.username))
            c.logout()

        c.force_login(self.user_manager)
        self.assertNotContains(c.get(url_list), 'Periodo de Permutas no activo', msg_prefix='manager user cannot access list outside period')
        c.logout()

        self.period_active()

    def test_list_view_answered_offers_access(self):
        '''TradeOffer list view restricts access properly for offers with accepted answers'''

        c = Client()

        url_list = reverse('trading:list')

        offers = ['Oferta #1', 'Oferta #2']

        for offer in offers:
            self.assertContains(c.get(url_list), offer, msg_prefix='anonymous user cannot see {} in list'.format(offer))

        for user in self.users:
            for offer in offers:
                self.assertContains(c.get(url_list), offer, msg_prefix='user {} cannot see {} in list'.format(user, offer))

        self.offer_accept_answer()

        self.assertNotContains(c.get(url_list), 'Oferta #1', msg_prefix='anonymous user can see answered offer in list')
        self.assertContains(c.get(url_list), 'Oferta #2', msg_prefix='anonymous user cannot see not answered offer in list')

        for user in [self.user1, self.user2]:
            c.force_login(user)
            self.assertContains(c.get(url_list), 'Oferta #1', msg_prefix='{} cannot see its answered offer in list'.format(user.username))
            self.assertContains(c.get(url_list), 'Oferta #2', msg_prefix='{} cannot see not answered offer in list'.format(user.username))
            c.logout()

        for user in [self.user3, self.user4]:
            c.force_login(user)
            self.assertNotContains(c.get(url_list), 'Oferta #1', msg_prefix='{} can see others answered offer in list'.format(user.username))
            self.assertContains(c.get(url_list), 'Oferta #2', msg_prefix='{} cannot see not answered offer in list'.format(user.username))
            c.logout()

        self.offer_remove_answer()

    def test_tradeoffer_views_access(self):
        '''TradeOffer CRUD views restrict access properly'''

        c = Client()

        # create
        url_create = reverse('trading:offer_create')

        res = c.get(url_create)
        self.assertEqual(res.status_code, 302, 'anonymous user can access create offer view')

        for user in self.users:
            c.force_login(user)
            res = c.get(url_create)
            self.assertEqual(res.status_code, 200, 'user {} cannot access create offer view'.format(user.username))
            c.logout()

        # read
        detail_url = self.offer.get_absolute_url()
        self.assertEqual(c.get(detail_url).status_code, 200, 'anonymous user cannot access offer detail view')

        for user in self.users:
            c.force_login(user)
            self.assertEqual(c.get(detail_url).status_code, 200, 'user {} cannot access offer detail view'.format(user.username))
            c.logout()

        # update and delete
        url_update = reverse('trading:offer_edit', args=[self.offer.id])
        url_delete = reverse('trading:offer_delete', args=[self.offer.id])

        self.assertEqual(c.get(url_update).status_code, 302, 'anonymous user is not redirected to login view')
        self.assertEqual(c.get(url_delete).status_code, 302, 'anonymous user is not redirected to login view')

        c.force_login(self.user1)
        self.assertEqual(c.get(url_update).status_code, 200, 'offer creator cannot access their offer editor')
        self.assertEqual(c.get(url_delete).status_code, 200, 'offer creator cannot access their offer editor')
        c.logout()

        for user in [self.user2, self.user3, self.user_manager]:
            c.force_login(user)
            self.assertEqual(c.get(url_update).status_code, 403, 'user {} can access another user offer editor'. format(user.username))
            self.assertEqual(c.get(url_delete).status_code, 403, 'user {} can access another user offer editor'. format(user.username))
            c.logout()

    def test_tradeofferanswer_views_access(self):
        '''TradeOfferAnswer CRUD views restrict access properly'''

        c = Client()

        # create
        url_create = reverse('trading:answer_create', args=[self.offer.id])

        self.assertEqual(c.get(url_create).status_code, 302, 'anonymous user can create answers')

        c.force_login(self.user1)
        self.assertContains(c.get(url_create), 'No puedes responder a tu propia oferta', status_code=403, msg_prefix='offer creator can create answer to its own offer')
        c.logout()

        c.force_login(self.user2)
        self.assertContains(c.get(url_create), 'Ya has respondido a esta oferta', status_code=403, msg_prefix='user with existing answer can create another answer')
        c.logout()

        c.force_login(self.user3)
        self.assertEqual(c.get(url_create).status_code, 200, 'random user cannot create answer')
        c.logout()

        # ensure access when other offers are in process
        self.offer2.answer = self.answer2
        self.offer2.save()

        c.force_login(self.user3)
        self.assertEqual(c.get(url_create).status_code, 200, 'random user cannot create answer if other offers are in process')
        c.logout()

        self.offer_remove_answer()

        # read
        read_url = self.answer.get_absolute_url()

        self.assertEqual(c.get(read_url).status_code, 302, 'anonymous user can read answer')

        c.force_login(self.user3)
        self.assertEqual(c.get(read_url).status_code, 403, 'random user can read answer')
        c.logout()

        users = [
            (self.user1, 'offer creator'),
            (self.user2, 'answer creator'),
            (self.user_manager, 'manager user'),
        ]

        for user in users:
            c.force_login(user[0])
            self.assertEqual(c.get(read_url).status_code, 200, '{} cannot read answer'.format(user[1]))
            c.logout()

        # update and delete
        url_update = reverse('trading:answer_edit', args=[self.answer.id])
        url_delete = reverse('trading:answer_delete', args=[self.answer.id])

        self.assertEqual(c.get(url_update).status_code, 302, 'anonymous user can update answer')
        self.assertEqual(c.get(url_delete).status_code, 302, 'anonymous user can delete answer')

        c.force_login(self.user1)
        self.assertEqual(c.get(url_update).status_code, 403, 'offer creator can update answer')
        self.assertEqual(c.get(url_delete).status_code, 403, 'offer creator can delete answer')
        c.logout()

        c.force_login(self.user2)
        self.assertEqual(c.get(url_update).status_code, 200, 'answer creator cannot update answer')
        self.assertEqual(c.get(url_delete).status_code, 200, 'answer creator cannot delete answer')
        c.logout()

        c.force_login(self.user3)
        self.assertEqual(c.get(url_update).status_code, 403, 'random user can update answer')
        self.assertEqual(c.get(url_delete).status_code, 403, 'random user can delete answer')
        c.logout()

    def test_answered_offer_views_access(self):
        '''Answered TradeOffer related views restrict access properly'''

        c = Client()

        self.offer_accept_answer()

        # read
        urls = [
            (self.offer.get_absolute_url(), 'answered offer detail view'),
            (self.offer.get_absolute_url(), 'accepted answer detail view'),
        ]

        for url in urls:
            self.assertEqual(c.get(url[0]).status_code, 302, 'anonymous user can access {}'.format(url[1]))

        for url, user in zip(urls, [self.user1, self.user2, self.user_manager]):
            c.force_login(user)
            self.assertEqual(c.get(url[0]).status_code, 200, 'user {} cannot access {}'.format(user.username, url[1]))
            c.logout()

        for url in urls:
            c.force_login(self.user3)
            self.assertEqual(c.get(url[0]).status_code, 403, 'random user can access {}'.format(url[1]))
            c.logout()

        # edit, delete
        urls = [
            (reverse('trading:offer_edit', args=[self.offer.id]), 'answered offer edit view'),
            (reverse('trading:offer_delete', args=[self.offer.id]), 'answered offer delete view'),
            (reverse('trading:answer_edit', args=[self.answer.id]), 'accepted answer edit view'),
            (reverse('trading:answer_delete', args=[self.answer.id]), 'accepted answer delete view'),
        ]

        for url in urls:
            self.assertEqual(c.get(url[0]).status_code, 302, 'anonymous user can access {}'.format(url[1]))

        for url, user in zip(urls, self.users):
            c.force_login(user)
            self.assertEqual(c.get(url[0]).status_code, 403, 'user {} can access {}'.format(user.username, url[1]))
            c.logout()

        self.offer_remove_answer()


class TradingUpdateViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester_1', email='test@test.com', password='1234')

        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=1)
        Subject.objects.create(code=2, name='Subject 2', acronym='S2', quarter=1, year=1)
        Subject.objects.create(code=3, name='Subject 3', acronym='S3', quarter=1, year=2)
        Subject.objects.create(code=4, name='Subject 4', acronym='S4', quarter=1, year=2)

        start = timezone.now() - timedelta(hours=1)
        end = timezone.now() + timedelta(hours=1)
        self.period = TradePeriod.objects.create(name='Period 1', start=start, end=end)

        self.offer = TradeOffer.objects.create(user=self.user, period=self.period, description='initial')

        self.line = TradeOfferLine.objects.create(
            offer=self.offer, year=1, subjects='1',
            curr_group=1, curr_subgroup=1, wanted_groups='2, 3'
        )

    def test_tradeoffer_edit_valid(self):
        '''TradeOffer update form works properly with valid input data'''

        c = Client()
        c.force_login(self.user)

        update_url = reverse('trading:offer_edit', args=[self.offer.id])

        # initial state
        data = {
            'description': 'initial',
            '0-curr_group': 1,
            '0-curr_subgroup': 1,
            '0-wanted_groups': [2],
            '0-subjects': [1],
        }

        res = c.post(update_url, data)

        self.assertEqual(TradeOffer.objects.count(), 1)
        self.assertEqual(self.offer.description, 'initial')
        self.assertEqual(TradeOfferLine.objects.count(), 1)
        self.assertListEqual(self.line.get_subjects_list(), [1])

        # description
        data['description'] = 'Hello World'
        res = c.post(update_url, data)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.description, 'Hello World', 'updated description does not change in object')

        # subjects
        data['0-subjects'] = [1, 2]
        res = c.post(update_url, data)

        self.line.refresh_from_db()
        self.assertListEqual(self.line.get_subjects_list(), [1, 2], 'updated subjects does not change in offer line')

        data['0-subjects'] = [2]
        res = c.post(update_url, data)

        self.line.refresh_from_db()
        self.assertListEqual(self.line.get_subjects_list(), [2], 'deleted subject still appears in offer line')

        # wanted groups
        data['0-wanted_groups'] = [2, 3]
        res = c.post(update_url, data)

        self.line.refresh_from_db()
        self.assertListEqual(self.line.get_wanted_groups(), [2, 3], 'updated wanted_groups does not change in offer line')

        data['0-wanted_groups'] = [3]
        res = c.post(update_url, data)

        self.line.refresh_from_db()
        self.assertListEqual(self.line.get_wanted_groups(), [3], 'deleted wanted group still appears in offer line')

        # current group and subgroup
        data['0-curr_group'] = 2
        data['0-curr_subgroup'] = 3
        res = c.post(update_url, data)

        self.line.refresh_from_db()
        self.assertEqual(self.line.curr_group, 2, 'updated current group does not change in offer line')
        self.assertEqual(self.line.curr_subgroup, 3, 'updated current subgroup does not change in offer line')

        # add line
        data['1-curr_group'] = 1
        data['1-curr_subgroup'] = 1
        data['1-wanted_groups'] = [2, 3]
        data['1-subjects'] = [3]

        res = c.post(update_url, data)

        self.assertEqual(TradeOfferLine.objects.count(), 2, 'new line is not created')

        # delete initial line
        data['0-subjects'] = []
        res = c.post(update_url, data)

        self.assertEqual(TradeOfferLine.objects.count(), 1, 'initial line is not deleted')


class TradingProcessTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='tester_1', email='test@test.com', password='1234')
        self.user2 = User.objects.create(username='tester_2', email='test2@test.com', password='1234')
        self.user3 = User.objects.create(username='tester_3', email='test3@test.com', password='1234')
        self.user4 = User.objects.create(username='tester_4', email='test4@test.com', password='1234')

        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=2)

        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() + timedelta(hours=1)
        self.period = TradePeriod.objects.create(name='Period 1', start=start, end=end)

        self.offer1 = TradeOffer.objects.create(user=self.user1, period=self.period)

        TradeOfferLine.objects.create(
            offer=self.offer1, year=1, subjects='1',
            curr_group=1, curr_subgroup=1, wanted_groups='2, 3'
        )

        self.offer2 = TradeOffer.objects.create(user=self.user4, period=self.period)

        TradeOfferLine.objects.create(
            offer=self.offer2, year=2, subjects='1',
            curr_group=1, curr_subgroup=1, wanted_groups='2, 3'
        )

        self.answer1 = TradeOfferAnswer(user=self.user2, offer=self.offer1)
        self.answer1.set_groups({'1': [2, 1]})
        self.answer1.save()

        self.answer2 = TradeOfferAnswer(user=self.user1, offer=self.offer2)
        self.answer2.set_groups({'1': [2, 1]})
        self.answer2.save()

    def test_answer_posts(self):
        '''TradeOfferAnswer views work properly with valid input in POST requests'''

        c = Client()
        c.force_login(self.user2)

        # delete existing answer
        self.assertRedirects(c.post(reverse('trading:answer_delete', args=[self.answer1.id])), reverse('trading:list'), msg_prefix='answer creator cannot delete answer')

        self.assertEqual(TradeOfferAnswer.objects.filter(pk=self.answer1.id).count(), 0, 'deleted answer still exists')

        # create another answer
        res = c.post(reverse('trading:answer_create', args=[self.offer1.id]), {'0-group': '2', '0-subgroup': '1'})

        self.assertEqual(TradeOfferAnswer.objects.filter(offer=self.offer1).count(), 1, 'created answer does not exist')

        self.answer1 = TradeOfferAnswer.objects.filter(offer=self.offer1).first()

        self.assertRedirects(res, reverse('trading:answer_detail', args=[self.answer1.id]), msg_prefix='answer creator cannot create answer after deleting the existing one')

        self.assertEqual(c.get(self.answer1.get_absolute_url()).status_code, 200, 'answer creator cannot read answer after creating it')

        # update new answer
        res = c.post(reverse('trading:answer_edit', args=[self.answer1.id]), {'0-group': '3', '0-subgroup': '2'})
        self.assertEqual(res.status_code, 200, 'valid post data generates error')
        self.assertContains(res, 'Respuesta actualizada correctamente.', msg_prefix='successful update does not show notification')

        self.answer1.refresh_from_db()

        self.assertDictEqual(self.answer1.get_groups(), {'1': [3, 2]}, 'updated data does not change object data')

        # accept answer
        c.logout()
        c.force_login(self.user1)

        res = c.post(reverse('trading:answer_accept', args=[self.answer1.id]), {})

        self.offer1.refresh_from_db()
        self.offer2.refresh_from_db()
        self.answer1.refresh_from_db()
        self.answer2.refresh_from_db()

        self.assertRedirects(res, reverse('trading:change_process', args=[self.offer1.id]), msg_prefix='valid answer cannot be accepted by offer creator')
        self.assertEqual(self.offer1.answer, self.answer1, 'accepted answer is not saved in the offer')
        self.assertFalse(self.offer1.is_visible, 'answered offer is still visible')
        self.assertTrue(self.offer2.is_visible, 'random offer is affected by another offer process')
        self.assertTrue(self.answer1.is_visible, 'accepted answer is hidden after it is accepted')
        self.assertFalse(self.answer2.is_visible, 'answer from answered offer creator is not hidden')

        # restore modified data
        self.offer1.answer = None
        self.offer1.save()

        self.answer2.is_visible = True
        self.answer2.save()


class TradingAuxiliarToolsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='tester_1', email='test@test.com', password='1234')
        self.user2 = User.objects.create(username='tester_2', email='test2@test.com', password='1234')

        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=1)

        now = timezone.now()
        period = TradePeriod.objects.create(name='Period 1', start=now - timedelta(hours=2), end=now + timedelta(hours=1))

        self.offer = TradeOffer.objects.create(user=self.user1, period=period)

        TradeOfferLine.objects.create(
            offer=self.offer, year=1, subjects='1',
            curr_group=1, curr_subgroup=1, wanted_groups='2'
        )

        answer = TradeOfferAnswer(user=self.user2, offer=self.offer)
        answer.set_groups({'1': [2, 1]})
        answer.save()

    def render_get_answer(self, offer, user):
        template_str = '{% load trading_tags %}{{ offer|get_answer:user }}'
        context = Context({'offer': offer, 'user': user})
        return Template(template_str).render(context)

    def test_templatetags_get_answer(self):
        '''get_answer template tag works as expected'''

        self.assertEquals(self.render_get_answer(self.offer, AnonymousUser()), 'None')
        self.assertEquals(self.render_get_answer(self.offer, self.user1), 'None')
        self.assertEquals(self.render_get_answer(self.offer, self.user2), 'Respuesta de {} para Oferta #1'.format(str(self.user2)))
