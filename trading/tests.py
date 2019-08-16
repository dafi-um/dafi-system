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

    def test_validation_offer_and_lines(self):
        '''Trade offers and their lines are properly created'''

        user = User.objects.get()
        year = Year.objects.get(pk=1)
        period = TradePeriod.objects.get()

        offer = TradeOffer(user=user, period=period)

        try:
            offer.full_clean()
        except Exception:
            self.fail('TradeOffer full_clean failed unexpectedly')

        offer.save()
        self.assertEqual(offer.id, 1)

        line = TradeOfferLine(offer=offer, year=year)

        self.assertRaises(ValidationError, line.full_clean)

        line.subjects = '3'
        line.curr_group = '3'
        line.curr_subgroup = '3'
        line.wanted_groups = '3'

        self.assertRaises(ValidationError, line.full_clean)

        try:
            line.full_clean()
        except ValidationError as e:
            errors = e.message_dict

        self.assertIn('subjects', errors, 'non-existing subject')
        self.assertIn('curr_group', errors, 'group out of range')
        self.assertIn('curr_subgroup', errors, 'subgroup out of range')
        self.assertIn('wanted_groups', errors, 'wanted group out of range')

        try:
            line.subjects = '2'
            line.full_clean()
        except ValidationError as e:
            errors = e.message_dict

        self.assertIn('subjects', errors, 'subject from another year')

        try:
            line.subjects = '1'
            line.full_clean()
        except ValidationError as e:
            errors = e.message_dict

        self.assertNotIn('subjects', errors, 'valid subject')

        try:
            line.curr_group = '1'
            line.curr_subgroup = '1'
            line.full_clean()
        except ValidationError as e:
            errors = e.message_dict

        self.assertNotIn('curr_group', errors, 'valid group')
        self.assertNotIn('curr_subgroup', errors, 'valid subgroup')

        try:
            line.wanted_groups = '1'
            line.full_clean()
        except ValidationError as e:
            errors = e.message_dict

        self.assertIn('wanted_groups', errors, 'wanted group equals current group')

        try:
            line.wanted_groups = '2'
            line.full_clean()
        except ValidationError as e:
            self.fail('Line validation failed unexpectedly')
