from datetime import timedelta

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from heart.models import Subject, Year

from .models import TradeOffer, TradeOfferLine, TradePeriod

User = get_user_model()


class TradeOfferTestCase(TestCase):
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
