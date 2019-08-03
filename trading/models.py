from django.contrib.auth import get_user_model
from django.db import models

from heart.models import Subject


class TradePeriod(models.Model):
    '''
    Trading allowed Period
    '''

    name = models.CharField('nombre', max_length=120)
    start = models.DateTimeField('fecha de inicio')
    end = models.DateTimeField('fecha de fin')

    def __str__(self):
        return 'Periodo ' + self.name

    class Meta:
        verbose_name = 'periodo de intercambio'
        verbose_name_plural = 'periodos de intercambio'


class TradeOffer(models.Model):
    '''
    Trading Offer
    '''

    OFFER_STATUS = [
        ('created', 'Oferta creada'),
        ('answered', 'Hay respuestas'),
        ('accepted', 'Respuesta aceptada'),
        ('completed', 'Proceso completado'),
    ]

    user = models.ForeignKey(get_user_model(), models.PROTECT, verbose_name='usuario')
    period = models.ForeignKey(TradePeriod, models.PROTECT, verbose_name='periodo')
    pub_date = models.DateTimeField('fecha de creación', auto_now_add=True)
    answer = models.ForeignKey('self', models.PROTECT, 'answers', blank=True, null=True, verbose_name='respuesta')
    is_answer = models.BooleanField('es una respuesta', default=False, help_text='Esta oferta es una respuesta a otra oferta')
    completed = models.BooleanField('proceso completado', default=False, help_text='El usuario ha completado su parte')

    def __str__(self):
        return 'Oferta {}: {} en {}'.format(self.id, self.user, self.period.name)

    class Meta:
        verbose_name = 'oferta de permuta'
        verbose_name_plural = 'ofertas de permuta'


class TradeOfferLine(models.Model):
    '''
    Trading Offer Line
    '''

    offer = models.ForeignKey(TradeOffer, on_delete=models.PROTECT, related_name='lines', verbose_name='oferta')
    year = models.IntegerField('año')
    subjects = models.CharField('asignaturas', max_length=64)
    curr_group = models.IntegerField('grupo actual')
    curr_subgroup = models.IntegerField('subgrupo actual')
    wanted_groups = models.CharField('grupos buscados', max_length=10)

    def get_subjects(self):
        return Subject.objects.filter(pk__in=self.subjects.split(','))

    def set_subjects(self, value):
        if value is None or len(value) < 1:
            self.subjects = ''
        elif isinstance(value, models.QuerySet):
            self.subjects = ','.join(str(x.id) for x in value)
        else:
            self.subjects = ','.join(str(x) for x in value)

    def get_wanted_groups(self):
        if self.wanted_groups is None or len(self.wanted_groups) < 1:
            return []

        return [int(x) for x in self.wanted_groups.split(',')]

    def get_wanted_groups_str(self):
        return ' ó '.join(x for x in self.wanted_groups.split(','))

    def set_wanted_groups(self, value):
        if value is None or len(value) < 1:
            self.wanted_groups = ''
        else:
            self.wanted_groups = ','.join(str(x) for x in value)

    def __str__(self):
        return 'Línea oferta {}: {} (grupo {}.{} a grupo(s) {})'.format(self.offer.id, self.subjects, self.curr_group, self.curr_subgroup, self.wanted_groups)

    class Meta:
        ordering = ['year']

        verbose_name = 'línea de oferta de permuta'
        verbose_name_plural = 'líneas de oferta de permuta'
