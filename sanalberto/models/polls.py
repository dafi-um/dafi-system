from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property

from .event import (
    Event,
    date_in_range,
)


class Poll(models.Model):
    """Designs poll.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Poll]'

    designs: 'models.Manager[PollDesign]'

    votes: 'models.Manager[PollVote]'

    event: 'models.ForeignKey[Event, Event]' = models.ForeignKey(
        Event, models.CASCADE, 'polls',
        verbose_name='evento'
    )

    title: 'models.CharField[str, str]' = models.CharField(
        'título', max_length=140
    )

    slug: 'models.SlugField[str, str]' = models.SlugField(
        max_length=140
    )

    register_start: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'inicio de registro'
    )

    register_end: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fin de registro'
    )

    voting_start: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'inicio de votación'
    )

    voting_end: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fin de votación'
    )

    winner: 'models.ForeignKey[PollDesign | None, PollDesign | None]' = models.ForeignKey(
        'PollDesign', models.CASCADE, 'won_polls',
        blank=True, null=True,
        verbose_name='diseño ganador',
    )

    class Meta:
        verbose_name = 'encuesta'

    def __str__(self) -> str:
        return f'#{self.id} {self.title}'

    @cached_property
    def register_enabled(self) -> bool:
        return date_in_range(self.register_start, self.register_end)

    @cached_property
    def voting_enabled(self) -> bool:
        return date_in_range(self.voting_start, self.voting_end)


class PollDesign(models.Model):
    """Poll design option.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[PollDesign]'

    votes: 'models.Manager[PollVote]'

    poll: 'models.ForeignKey[Poll, Poll]' = models.ForeignKey(
        Poll, models.CASCADE, 'designs',
        verbose_name='encuesta'
    )

    user: 'models.ForeignKey[AbstractUser, AbstractUser]' = models.ForeignKey(
        get_user_model(), models.PROTECT,
        verbose_name='creador'
    )

    title = models.CharField(
        'título', max_length=128
    )

    image: 'models.ImageField' = models.ImageField(
        'imagen', upload_to='designs/'
    )

    voting_image: 'models.ImageField' = models.ImageField(
        'imagen de votación', upload_to='designs-tshirts/',
        help_text='Esta imagen se mostrará solamente en el formulario de votación',
        blank=True,
    )

    source_file: 'models.FileField' = models.FileField(
        'fichero fuente', upload_to='designs-sources/'
    )

    vector_file: 'models.FileField' = models.FileField(
        'fichero del vectorizado', upload_to='designs-vectors/'
    )

    is_approved: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'diseño aprobado', default=False
    )

    created: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    class Meta:
        verbose_name = 'diseño'

        ordering = ('-created', 'title')

    def __str__(self) -> str:
        return f'Diseño #{self.id} `{self.title}` de {self.user}'

    @property
    def voting_image_url(self) -> 'models.ImageField':
        return self.voting_image.url if self.voting_image else self.image.url


class PollVote(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[PollVote]'

    poll: 'models.ForeignKey[Poll, Poll]' = models.ForeignKey(
        Poll, models.CASCADE, 'votes',
        verbose_name='encuesta'
    )

    user: 'models.ForeignKey[AbstractUser, AbstractUser]' = models.ForeignKey(
        get_user_model(), models.SET_NULL, 'designs_voted',
        null=True, # To allow user deletion without loosing votes
        verbose_name='votante'
    )

    first: 'models.ForeignKey[PollDesign, PollDesign]' = models.ForeignKey(
        PollDesign, models.CASCADE, 'votes_first',
        verbose_name='diseño prioridad 1',
    )

    second: 'models.ForeignKey[PollDesign, PollDesign]' = models.ForeignKey(
        PollDesign, models.CASCADE, 'votes_second',
        blank=True, null=True,
        verbose_name='diseño prioridad 2',
    )

    third: 'models.ForeignKey[PollDesign, PollDesign]' = models.ForeignKey(
        PollDesign, models.CASCADE, 'votes_third',
        blank=True, null=True,
        verbose_name='diseño prioridad 3',
    )

    created: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fecha de creación', auto_now_add=True,
    )

    updated: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'última actualización', auto_now=True,
    )

    class Meta:
        verbose_name = 'voto'

    def __str__(self) -> str:
        return f'Voto #{self.id}'
