from datetime import timedelta

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import reverse
from django.template import Context, Template
from django.test import Client, TestCase
from django.utils import timezone

from heart.models import Subject, Year

from .models import TradeOffer, TradeOfferAnswer, TradeOfferLine, TradePeriod

User = get_user_model()


class TradingModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester', email='test@test.com', password='1234')

        self.year1 = Year.objects.create(id=1, groups=2, subgroups=2)
        self.year2 = Year.objects.create(id=2, groups=3, subgroups=3)

        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=self.year1)
        Subject.objects.create(code=2, name='Subject 2', acronym='S2', quarter=1, year=self.year2)

        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() + timedelta(hours=2)

        self.period = TradePeriod.objects.create(name='Period 1', start=start, end=end)

    def test_tradeofferline_getters(self):
        '''TradeOfferLine getters return correct values'''

        line = TradeOfferLine()

        # wanted groups
        line.wanted_groups = ''
        self.assertEquals(line.get_wanted_groups(), [])
        self.assertEquals(line.get_wanted_groups_str(), '')

        line.wanted_groups = '1'
        self.assertEquals(line.get_wanted_groups(), [1])
        self.assertEquals(line.get_wanted_groups_str(), '1')

        line.wanted_groups = '1,2'
        self.assertEquals(line.get_wanted_groups(), [1,2])
        self.assertEquals(line.get_wanted_groups_str(), '1 ó 2')

        line.wanted_groups = '1,a'
        self.assertEquals(line.get_wanted_groups(), [])
        self.assertEquals(line.get_wanted_groups_str(), '')

        line.wanted_groups = 'not_valid'
        self.assertEquals(line.get_wanted_groups(), [])
        self.assertEquals(line.get_wanted_groups_str(), '')

        # subjects
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

        line = TradeOfferLine(year=self.year1, curr_group=1, curr_subgroup=1, wanted_groups='2')

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

        line = TradeOfferLine(year=self.year1, curr_group=1, curr_subgroup=1, subjects='1')

        with self.assertRaisesMessage(ValidationError, 'Valor de grupos buscados inválido'):
            line.wanted_groups = 'not_valid'
            line.full_clean(['offer'])

        with self.assertRaisesMessage(ValidationError, 'El grupo 3 no existe en Año 1'):
            line.wanted_groups = '3'
            line.full_clean(['offer'])

        with self.assertRaisesMessage(ValidationError, 'El grupo 3 no existe en Año 1'):
            line.wanted_groups = '2,3'
            line.full_clean(['offer'])

        self.assertEquals(line.get_wanted_groups(), [2, 3], 'Comma separated list not parsed properly')

        with self.assertRaisesMessage(ValidationError, 'El grupo actual no puede estar en los grupos buscados'):
            line.wanted_groups = '1'
            line.full_clean(['offer'])

        try:
            line.wanted_groups = '2'
            line.full_clean(['offer'])
        except ValidationError:
            self.fail('Wanted groups is valid but validation failed')

        with self.assertRaisesMessage(ValidationError, 'El grupo 3 no existe en Año 1'):
            line.curr_group = '3'
            line.full_clean(['offer'])

        try:
            line.curr_group = '1'
            line.full_clean(['offer'])
        except ValidationError:
            self.fail('Current group is valid but validation failed')

        with self.assertRaisesMessage(ValidationError, 'El subgrupo 3 no existe en Año 1'):
            line.curr_subgroup = '3'
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

        TradeOfferLine.objects.create(offer=offer, year=self.year1, curr_group='1', curr_subgroup='1', wanted_groups='2', subjects='1')
        TradeOfferLine.objects.create(offer=offer, year=self.year2, curr_group='1', curr_subgroup='1', wanted_groups='2,3', subjects='2')

        answer = TradeOfferAnswer(offer=offer)

        for case in [{'1': [2, 1], '2': [2, 1]}, {'1': [2, 2], '2': [3, 3]}]:
            answer.set_groups(case)

            try:
                answer.full_clean(['user'])
            except ValidationError:
                self.fail('validation failed for valid data')

        cases = [
            ({}, 'This field cannot be blank.'),
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
            ({'1': [2, 0], '2': [2, 1]}, 'El subgrupo 0 no existe en Año 1'),
            ({'1': [2, 3], '2': [2, 1]}, 'El subgrupo 3 no existe en Año 1'),
            ({'1': [2, 1], '2': [2, 4]}, 'El subgrupo 4 no existe en Año 2'),
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

        year = Year.objects.create(id=1, groups=2, subgroups=2)

        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=year)

        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() + timedelta(hours=1)
        self.period = TradePeriod.objects.create(name='Period 1', start=start, end=end)

        self.offer = TradeOffer.objects.create(user=self.user1, period=self.period)

        TradeOfferLine.objects.create(
            offer=self.offer, year=year, subjects='1',
            curr_group=1, curr_subgroup=1, wanted_groups='2'
        )

        self.create_answer()

    def create_answer(self):
        self.answer = TradeOfferAnswer(user=self.user2, offer=self.offer)
        self.answer.set_groups({'1': [2, 1]})
        self.answer.save()

    def period_expired(self):
        self.period.end = timezone.now() - timedelta(hours=1)
        self.period.save()

    def period_active(self):
        self.period.end = timezone.now() + timedelta(hours=1)
        self.period.save()

    def test_tradeoffer_views_access(self):
        '''TradeOffer list and CRUD views restrict access properly'''

        c = Client()

        # list
        url_list = reverse('trading:list')

        self.assertNotContains(c.get(url_list), 'Periodo de Permutas no activo')

        self.period_expired()

        self.assertContains(c.get(url_list), 'Periodo de Permutas no activo')

        self.period_active()

        # create
        url_create = reverse('trading:offer_create')

        res = c.get(url_create)
        self.assertEqual(res.status_code, 302)

        c.force_login(self.user1)

        res = c.get(url_create)
        self.assertEqual(res.status_code, 200)

        c.logout()

        # read
        res = c.get(self.offer.get_absolute_url())
        self.assertEqual(res.status_code, 200)

        # update and delete
        url_update = reverse('trading:offer_edit', args=[self.offer.id])
        url_delete = reverse('trading:offer_delete', args=[self.offer.id])

        self.assertEqual(c.get(url_update).status_code, 302)
        self.assertEqual(c.get(url_delete).status_code, 302)

        c.force_login(self.user2)

        self.assertEqual(c.get(url_update).status_code, 403)
        self.assertEqual(c.get(url_delete).status_code, 403)

        c.force_login(self.user1)

        self.assertEqual(c.get(url_update).status_code, 200)
        self.assertEqual(c.get(url_delete).status_code, 200)

    def test_tradeofferanswer_views_access(self):
        '''TradeOfferAnswer CRUD views restrict access properly'''

        c = Client()

        # create
        url_create = reverse('trading:answer_create', args=[self.offer.id])

        self.assertEqual(c.get(url_create).status_code, 302, 'anonymous user can create answer')

        c.force_login(self.user1)
        self.assertEqual(c.get(url_create).status_code, 403, 'offer creator can create answer to its own offer')

        c.logout()

        c.force_login(self.user2)
        self.assertEqual(c.get(url_create).status_code, 403, 'user with existing answer can create another answer')

        c.logout()

        c.force_login(self.user3)
        self.assertEqual(c.get(url_create).status_code, 200, 'valid user cannot create answer')

        c.logout()

        # read
        read_url = self.answer.get_absolute_url()

        self.assertEqual(c.get(read_url).status_code, 302, 'anonymous user can read answers')

        c.force_login(self.user1)
        self.assertEqual(c.get(read_url).status_code, 200, 'offer creator cannot read answer')

        c.logout()

        c.force_login(self.user2)
        self.assertEqual(c.get(read_url).status_code, 200, 'answer creator cannot read answer')

        c.logout()

        c.force_login(self.user3)
        self.assertEqual(c.get(read_url).status_code, 403, 'invalid user can read answer')

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
        c.force_login(self.user3)

        self.assertEqual(c.get(url_update).status_code, 403, 'invalid user can update answer')
        self.assertEqual(c.get(url_delete).status_code, 403, 'invalid user can delete answer')

        c.logout()
        c.force_login(self.user2)

        self.assertEqual(c.get(url_update).status_code, 200, 'answer creator cannot update answer')
        self.assertEqual(c.get(url_delete).status_code, 200, 'answer creator cannot delete answer')

    def test_tradeofferanswer_views_post(self):
        '''TradeOfferAnswer views work properly with valid input in POST requests'''

        c = Client()

        url_create = reverse('trading:answer_create', args=[self.offer.id])
        url_update = reverse('trading:answer_edit', args=[self.answer.id])
        url_delete = reverse('trading:answer_delete', args=[self.answer.id])

        self.assertEqual(c.post(url_update).status_code, 200, 'answer creator cannot update answer')
        self.assertRedirects(c.post(url_delete), reverse('trading:list'), msg_prefix='answer creator cannot delete answer')

        self.assertEqual(c.get(url_create).status_code, 200, 'answer creator cannot create answer after deleting the existing one')

        self.create_answer()

        self.assertEqual(c.get(self.answer.get_absolute_url()).status_code, 200, 'answer creator cannot read answer after re-creating it')


class TradingAuxiliarToolsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='tester_1', email='test@test.com', password='1234')
        self.user2 = User.objects.create(username='tester_2', email='test2@test.com', password='1234')

        year = Year.objects.create(id=1, groups=2, subgroups=2)

        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=year)

        now = timezone.now()
        period = TradePeriod.objects.create(name='Period 1', start=now - timedelta(hours=2), end=now + timedelta(hours=1))

        self.offer = TradeOffer.objects.create(user=self.user1, period=period)

        TradeOfferLine.objects.create(
            offer=self.offer, year=year, subjects='1',
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
        self.assertEquals(self.render_get_answer(self.offer, self.user2), 'Respuesta de tester_2 para Oferta #1')
