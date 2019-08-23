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
        User.objects.create(username='tester', email='test@test.com', password='1234')

        Year.objects.create(id=1, groups=2, subgroups=2)
        Year.objects.create(id=2, groups=2, subgroups=2)
        Subject.objects.create(code=1, name='Subject 1', acronym='S1', quarter=1, year=Year.objects.get(pk=1))
        Subject.objects.create(code=2, name='Subject 2', acronym='S2', quarter=1, year=Year.objects.get(pk=2))

        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() + timedelta(hours=2)

        TradePeriod.objects.create(name='Period 1', start=start, end=end)

    def test_tradeofferline_validate_subjects(self):
        '''TradeOfferLine validates subjects properly'''

        year = Year.objects.get(pk=1)

        line = TradeOfferLine(year=year, curr_group=1, curr_subgroup=1, wanted_groups='2')

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

        year = Year.objects.get(pk=1)

        line = TradeOfferLine(year=year, curr_group=1, curr_subgroup=1, subjects='1')

        with self.assertRaisesMessage(ValidationError, 'Valor de grupos buscados inválido'):
            line.wanted_groups = 'not_valid'
            line.full_clean(['offer'])

        self.assertEquals(line.get_wanted_groups(), [])

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
