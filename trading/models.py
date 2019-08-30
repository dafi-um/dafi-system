import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from heart.models import Subject, Year


class TradePeriod(models.Model):
    '''
    Trading allowed Period
    '''

    name = models.CharField('nombre', max_length=120)
    start = models.DateTimeField('fecha de inicio')
    end = models.DateTimeField('fecha de fin')

    @classmethod
    def get_current(cls):
        now = timezone.now()
        return cls.objects.filter(start__lt=now, end__gt=now).first()

    def __str__(self):
        return 'Periodo ' + self.name

    class Meta:
        verbose_name = 'periodo de intercambio'
        verbose_name_plural = 'periodos de intercambio'


class TradeOffer(models.Model):
    '''
    Trading Offer
    '''

    user = models.ForeignKey(get_user_model(), models.PROTECT, verbose_name='usuario')
    period = models.ForeignKey(TradePeriod, models.PROTECT, verbose_name='periodo')
    creation_date = models.DateTimeField('fecha de creación', auto_now_add=True)
    answer = models.ForeignKey('TradeOfferAnswer', models.PROTECT, blank=True, null=True, verbose_name='respuesta')
    is_visible = models.BooleanField('es visible', default=True, help_text='La oferta es visible para otros usuarios y puede recibir respuestas')
    is_completed = models.BooleanField('proceso completado', default=False, help_text='El usuario ha completado su parte')

    class Meta:
        verbose_name = 'oferta de permuta'
        verbose_name_plural = 'ofertas de permuta'

        ordering = ['id']

        permissions = [
            ('is_manager', 'Puede ver cualquier oferta y acceder a las vistas de gestión de ofertas'),
        ]

    def __str__(self):
        return 'Oferta {}: {} en {}'.format(self.id, self.user, self.period.name)

    def get_absolute_url(self):
        return reverse('trading:offer_detail', kwargs={'pk': self.pk})


class TradeOfferLine(models.Model):
    '''
    Trading Offer Line representing all the subjects in a year
    '''

    offer = models.ForeignKey(TradeOffer, on_delete=models.PROTECT, related_name='lines', verbose_name='oferta')
    year = models.ForeignKey(Year, on_delete=models.PROTECT, related_name='year', verbose_name='año')
    subjects = models.CharField('asignaturas', max_length=64)
    curr_group = models.IntegerField('grupo actual', default=1)
    curr_subgroup = models.IntegerField('subgrupo actual', default=1)
    wanted_groups = models.CharField('grupos buscados', max_length=10, default='')

    class Meta:
        ordering = ['year']

        verbose_name = 'línea de oferta de permuta'
        verbose_name_plural = 'líneas de oferta de permuta'

    def __str__(self):
        return 'Línea oferta {}: {} (grupo {}.{} a grupo(s) {})'.format(self.offer.id, self.subjects, self.curr_group, self.curr_subgroup, self.wanted_groups)

    def clean(self):
        errors = {}

        if self.curr_subgroup < 1 or self.curr_subgroup > self.year.subgroups:
            errors['curr_subgroup'] = 'El subgrupo {} no existe en {}'.format(self.curr_subgroup, self.year)

        if self.curr_group < 1 or self.curr_group > self.year.groups:
            errors['curr_group'] = 'El grupo {} no existe en {}'.format(self.curr_group, self.year)

        if self.wanted_groups:
            l = self.get_wanted_groups()

            if not l:
                errors['wanted_groups'] = 'Valor de grupos buscados inválido'
            elif self.curr_group in l:
                errors['wanted_groups'] = 'El grupo actual no puede estar en los grupos buscados'
            else:
                for g in l:
                    if g < 1 or g > self.year.groups:
                        errors['curr_group'] = 'El grupo {} no existe en {}'.format(g, self.year)

        if self.subjects:
            l = len(self.get_subjects_list())

            if l:
                q = self.get_subjects()

                if q.count() != l:
                    errors['subjects'] = 'Código de asignatura incorrecto'

                for s in q:
                    if s.year != self.year:
                        errors['subjects'] = 'La asignatura {} es de un año distinto'.format(s.code)
            else:
                errors['subjects'] = 'Valor de asignaturas inválido'

        if errors:
            raise ValidationError(errors)

        return super().clean()

    def get_subjects_list(self):
        try:
            return [int(x) for x in self.subjects.split(',')]
        except ValueError as e:
            return []

    def get_subjects(self):
        return Subject.objects.filter(pk__in=self.get_subjects_list())

    def get_wanted_groups(self):
        try:
            return [int(x) for x in self.wanted_groups.split(',')]
        except ValueError as e:
            return []

    def get_wanted_groups_str(self):
        return ' ó '.join(str(x) for x in self.get_wanted_groups())

    @cached_property
    def i(self):
        return self.year.i

class TradeOfferAnswer(models.Model):
    '''
    Trade Offer Answer
    '''

    offer = models.ForeignKey(TradeOffer, models.PROTECT, 'answers', verbose_name='oferta')
    user = models.ForeignKey(get_user_model(), models.PROTECT, verbose_name='usuario')
    groups = models.CharField('grupos ofertados', max_length=64)
    creation_date = models.DateTimeField('fecha de creación', auto_now_add=True)
    is_completed = models.BooleanField('proceso completado', default=False, help_text='El usuario ha completado su parte')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._groups = {}

    class Meta():
        verbose_name = 'respuesta de oferta de permuta'
        verbose_name_plural = 'respuestas de oferta de permuta'

    def __str__(self):
        return 'Respuesta de {} para Oferta #{}'.format(self.user, self.offer.id)

    def get_absolute_url(self):
        return reverse('trading:answer_detail', args=[self.pk])

    def clean(self):
        if not self.groups:
            return super().clean()

        groups = self.get_groups()

        if not groups:
            raise ValidationError({'groups': 'Valor de grupos ofertados inválido'})

        for line in self.offer.lines.all():
            year_key = str(line.year.id) # because JSON dictionary keys are always strings

            if year_key not in groups:
                raise ValidationError({'groups': 'No hay un valor para {}'.format(line.year)})
            elif not isinstance(groups[year_key], list):
                raise ValidationError({'groups': 'Formato incorrecto para {}'.format(line.year)})

            try:
                group, subgroup = groups[year_key]
            except ValueError:
                raise ValidationError({'groups': 'Formato incorrecto para {}'.format(line.year)})

            if group not in line.get_wanted_groups():
                raise ValidationError({'groups': 'El grupo {} no es un grupo buscado'.format(group)})

            if subgroup < 1 or subgroup > line.year.subgroups:
                raise ValidationError({'groups': 'El subgrupo {} no existe en {}'.format(subgroup, line.year)})

        return super().clean()

    def set_groups(self, value):
        self._groups = value
        self.groups = json.dumps(value, separators=(',', ':')) if value else ''

    def get_groups(self):
        if self.groups and not self._groups:
            self._groups = json.loads(self.groups)

        return self._groups

    def get_lines(self):
        l = []

        if not self.offer: return l

        groups = self.get_groups()

        for line in self.offer.lines.all():
            group, subgroup = groups[str(line.year.id)]

            l.append({
                'line': line,
                'year': line.year,
                'curr_group': line.curr_group,
                'curr_subgroup': line.curr_subgroup,
                'new_group': group,
                'new_subgroup': subgroup,
            })

        return l
