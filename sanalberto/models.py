from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from clubs.models import Club

def date_in_range(start, end):
    now = timezone.now()

    return start <= now and now < end


class Event(models.Model):
    '''
    Year event.

    Groups entities related to a specific year.
    '''

    date = models.DateField('fecha')

    design_register_start = models.DateTimeField(
        'inicio de registro de diseños'
    )

    design_register_end = models.DateTimeField(
        'fin de registro de diseños'
    )

    design_poll_start = models.DateTimeField(
        'inicio de elección de diseños'
    )

    design_poll_end = models.DateTimeField(
        'fin de elección de diseños'
    )

    selling_start = models.DateTimeField(
        'inicio de venta de productos'
    )

    selling_end = models.DateTimeField(
        'fin de venta de productos'
    )

    winner_design = models.ForeignKey(
        'Design', models.CASCADE, 'events_won',
        blank=True, null=True, verbose_name='diseño ganador'
    )

    def __str__(self):
        return 'San Alberto de {}'.format(self.date.year)

    class Meta:
        verbose_name = 'evento'

    def design_register_enabled(self):
        return date_in_range(self.design_register_start, self.design_register_end)

    def design_poll_enabled(self):
        return date_in_range(self.design_poll_start, self.design_poll_end)

    def shop_enabled(self):
        return date_in_range(self.selling_start, self.selling_end)


class Activity(models.Model):
    '''
    Event activity
    '''

    title = models.CharField('título', max_length=120)

    description = models.TextField('descripción')

    event = models.ForeignKey(
        Event, models.CASCADE,
        verbose_name='evento'
    )

    organiser = models.ForeignKey(
        get_user_model(), models.SET_NULL, blank=True, null=True,
        verbose_name='usuario organizador'
    )

    club = models.ForeignKey(
        Club, models.CASCADE, blank=True, null=True,
        verbose_name='club organizador'
    )

    start = models.DateTimeField('inicio')

    end = models.DateTimeField('fin')

    class Meta:
        verbose_name = 'actividad'
        verbose_name_plural = 'actividades'


class Design(models.Model):
    '''T-shirt design'''

    event = models.ForeignKey(
        Event, models.CASCADE,
        verbose_name='evento'
    )

    user = models.ForeignKey(
        get_user_model(), models.PROTECT,
        verbose_name='creador'
    )

    title = models.CharField('título', max_length=128)

    image = models.ImageField(
        'imagen pública', upload_to='designs/'
    )

    source_file = models.FileField(
        'fichero fuente', upload_to='designs-sources/'
    )

    is_approved = models.BooleanField(
        'diseño aprobado', default=False
    )

    created = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    class Meta:
        verbose_name = 'diseño'

        ordering = ('-created', 'title')

    def __str__(self):
        return 'Diseño #{} `{}` de {}'.format(self.pk, self.title, self.user)
