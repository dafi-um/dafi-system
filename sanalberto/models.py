from django.contrib.auth import get_user_model
from django.db import models

from clubs.models import Club


class Event(models.Model):
    '''
    Year event.

    Groups entities related to a specific year.
    '''

    date = models.DateTimeField('fecha')

    class Meta:
        verbose_name = 'evento'


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
