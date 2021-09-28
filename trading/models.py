import json

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    int_list_validator,
)
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property


class Subject(models.Model):
    """
    Academic subject
    """

    id: 'models.AutoField[int, int]'

    QUARTERS = [
        (1, 'Primer cuatrimestre'),
        (2, 'Segundo cuatrimestre'),
    ]

    code = models.IntegerField('código', primary_key=True)

    name = models.CharField('nombre', max_length=64)

    acronym = models.CharField('siglas', max_length=6)

    quarter = models.IntegerField('cuatrimestre', choices=QUARTERS, default=1)

    year = models.IntegerField('año', validators=[
        MinValueValidator(1), MaxValueValidator(3)
    ])

    class Meta:
        verbose_name = 'asignatura'

    def __str__(self):
        return '{} {} ({})'.format(self.code, self.name, self.acronym)

    @classmethod
    def get_grouped(cls):
        d = cache.get('grouped_subjects')

        if not d:
            d = {}

            for s in cls.objects.all():
                if s.year not in d:
                    d[s.year] = []

                d[s.year].append(s)

            cache.set('grouped_subjects', d)

        return d


class Year:
    """Academic year"""

    def __init__(self, id, max_subgroups, groups):
        self.id = id
        self.groups = groups
        self.groups_len = len(groups)
        self.groups_range = range(1, self.groups_len + 1)
        self.subgroups_range = range(1, max_subgroups + 1)

    def invalid_group(self, group):
        return group < 1 or group > self.groups_len

    def invalid_subgroup(self, group, subgroup):
        return subgroup < 1 or subgroup > self.groups[group]

    def subjects(self):
        return Subject.objects.filter(year=self.id)


YEARS = {
    1: Year(1, 3, {
        1: 3,
        2: 3,
        3: 3,
        4: 3,
    }),

    2: Year(2, 3, {
        1: 3,
        2: 3,
        3: 3,
    }),

    3: Year(3, 3, {
        1: 2,
        2: 3,
        3: 3,
    }),
}


class TradePeriod(models.Model):
    """
    Trading allowed Period
    """

    id: 'models.AutoField[int, int]'

    name = models.CharField('nombre', max_length=120)
    start = models.DateTimeField('fecha de inicio')
    end = models.DateTimeField('fecha de fin')

    class Meta:
        verbose_name = 'periodo de intercambio'
        verbose_name_plural = 'periodos de intercambio'

    def __str__(self):
        return self.name

    @classmethod
    def get_current(cls):
        now = timezone.now()
        return cls.objects.filter(start__lt=now, end__gt=now).first()

    @classmethod
    def get_next(cls):
        return cls.objects.order_by('start').first()


class TradeOffer(models.Model):
    """
    Trading Offer
    """

    id: 'models.AutoField[int, int]'

    user = models.ForeignKey(get_user_model(), models.CASCADE, verbose_name='usuario')
    period = models.ForeignKey(TradePeriod, models.CASCADE, verbose_name='periodo')
    answer = models.ForeignKey('TradeOfferAnswer', models.PROTECT, blank=True, null=True, verbose_name='respuesta')
    creation_date = models.DateTimeField('fecha de creación', auto_now_add=True)
    description = models.CharField('descripción', max_length=240, blank=True, default='')
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
    """
    Trading Offer Line representing all the subjects in a year
    """

    id: 'models.AutoField[int, int]'

    offer = models.ForeignKey(
        TradeOffer, on_delete=models.CASCADE, related_name='lines', verbose_name='oferta'
    )

    year = models.IntegerField('año', validators=[
        MinValueValidator(1), MaxValueValidator(3)
    ])

    subjects = models.CharField('asignaturas', max_length=64)

    started = models.CharField(
        'intercambios iniciados', max_length=64, blank=True, default='',
        validators=[int_list_validator()]
    )

    completed = models.CharField(
        'intercambios completados', max_length=64, blank=True, default='',
        validators=[int_list_validator()]
    )

    curr_group = models.IntegerField('grupo actual', default=1)

    curr_subgroup = models.IntegerField('subgrupo actual', default=1)

    wanted_groups = models.CharField('grupos buscados', max_length=10, default='')

    is_completed = models.BooleanField(
        'proceso completado', default=False,
        help_text='Todas las asignaturas de la línea se han intercambiado.'
    )

    class Meta:
        ordering = ['year']

        verbose_name = 'línea de oferta de permuta'
        verbose_name_plural = 'líneas de oferta de permuta'

    def __str__(self):
        return 'Línea oferta {}: {} (grupo {}.{} a grupo(s) {})'.format(self.offer.id, self.subjects, self.curr_group, self.curr_subgroup, self.wanted_groups)

    def clean(self):
        errors = {}

        y = YEARS[self.year]

        if y.invalid_group(self.curr_group):
            errors['curr_group'] = 'El grupo {} no existe en Año {}'.format(
                self.curr_group, self.year
            )
        elif y.invalid_subgroup(self.curr_group, self.curr_subgroup):
            errors['curr_subgroup'] = 'El subgrupo {}.{} no existe en Año {}'.format(
                self.curr_group, self.curr_subgroup, self.year
            )

        if self.wanted_groups:
            l = self.get_wanted_groups()

            if not l:
                errors['wanted_groups'] = 'Valor de grupos buscados inválido'
            elif self.curr_group in l:
                errors['wanted_groups'] = 'El grupo actual no puede estar en los grupos buscados'
            else:
                for g in l:
                    if y.invalid_group(g):
                        errors['curr_group'] = 'El grupo {} no existe en Año {}'.format(g, self.year)

        subjects_list = self.get_subjects_list()

        if subjects_list:
            subjects = self.get_subjects()

            if len(subjects) != len(subjects_list):
                errors['subjects'] = 'Código de asignatura incorrecto'
            else:
                for s in subjects:
                    if s.year != self.year:
                        errors['subjects'] = 'La asignatura {} es de un año distinto'.format(s.code)
        elif self.subjects:
            errors['subjects'] = 'Valor de asignaturas inválido'

        started_list = self.get_started_list()

        for subject in started_list:
            if subject not in subjects_list:
                errors['started'] = 'La asignatura {} no aparece en esta línea'.format(subject)

        if self.started and not started_list:
            errors['started'] = 'Valor de intercambios iniciados inválido'

        completed_list = self.get_completed_list()

        for subject in completed_list:
            if subject not in started_list:
                errors['completed'] = 'La asignatura {} no se está intercambiando'.format(subject)

        if self.completed and not completed_list:
            errors['completed'] = 'Valor de intercambios completados inválido'

        if errors:
            raise ValidationError(errors)

        return super().clean()

    def _get_list_from_str(self, field):
        try:
            return [int(x) for x in getattr(self, field).split(',')]
        except ValueError as e:
            return []

    def get_subjects_list(self):
        return self._get_list_from_str('subjects')

    def get_subjects(self):
        return Subject.objects.filter(pk__in=self.get_subjects_list())

    def get_started_list(self):
        return self._get_list_from_str('started')

    def get_started(self):
        return Subject.objects.filter(pk__in=self.get_started_list())

    def get_completed_list(self):
        return self._get_list_from_str('completed')

    def get_wanted_groups(self):
        try:
            return [int(x) for x in self.wanted_groups.split(',')]
        except ValueError as e:
            return []

    @cached_property
    def year_obj(self):
        return YEARS[self.year]

    @cached_property
    def i(self):
        return self.year - 1

class TradeOfferAnswer(models.Model):
    """
    Trade Offer Answer
    """

    id: 'models.AutoField[int, int]'

    offer = models.ForeignKey(
        TradeOffer, models.CASCADE, 'answers', verbose_name='oferta'
    )

    user = models.ForeignKey(
        get_user_model(), models.CASCADE, verbose_name='usuario'
    )

    groups = models.CharField('grupos ofertados', max_length=64)

    creation_date = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    is_visible = models.BooleanField(
        'es visible', default=True,
        help_text='La respuesta aparece en la oferta para la que fue creada.'
    )

    is_completed = models.BooleanField(
        'proceso completado', default=False,
        help_text='El usuario ha completado su parte.'
    )

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
            year_key = str(line.year) # because JSON dictionary keys are always strings

            if year_key not in groups:
                raise ValidationError({'groups': 'No hay un valor para Año {}'.format(line.year)})
            elif not isinstance(groups[year_key], list):
                raise ValidationError({'groups': 'Formato incorrecto para Año {}'.format(line.year)})

            try:
                group, subgroup = groups[year_key]
            except ValueError:
                raise ValidationError({'groups': 'Formato incorrecto para Año {}'.format(line.year)})

            if group not in line.get_wanted_groups():
                raise ValidationError({'groups': 'El grupo {} no es un grupo buscado'.format(group)})

            if YEARS[line.year].invalid_subgroup(group, subgroup):
                raise ValidationError({
                    'groups': 'El subgrupo {}.{} no existe en Año {}'.format(
                        group, subgroup, line.year
                    )
                })

        return super().clean()

    def set_groups(self, value):
        self._groups = value
        self.groups = json.dumps(value, separators=(',', ':')) if value else ''

    def get_groups(self):
        if self.groups and not self._groups:
            self._groups = json.loads(self.groups)

        return self._groups
