from django.contrib.auth import get_user_model
from django.db import models

from main.models import Subject


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
