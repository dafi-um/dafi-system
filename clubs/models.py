import typing
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static
from django.urls import reverse

from meta.models import ModelMeta


if typing.TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Club(ModelMeta, models.Model):
    """Club.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Club]'

    meetings: 'models.Manager[ClubMeeting]'

    name: 'models.CharField[str, str]' = models.CharField(
        'nombre', max_length=64
    )

    slug: 'models.SlugField[str, str]' = models.SlugField(
        'slug', max_length=64, unique=True
    )

    description: 'models.TextField[str, str]' = models.TextField(
        'descripción', max_length=300
    )

    document: 'models.FileField' = models.FileField(
        'documento', upload_to='clubs/docs/', blank=True,
        help_text='Útil para bases de concursos o información de actividades.'
    )

    document_name: 'models.CharField[str, str]' = models.CharField(
        'nombre del documento', max_length=120, default='', blank=True,
        help_text='Texto que aparecerá en el enlace del documento.'
    )

    image: 'models.ImageField' = models.ImageField(
        'imagen', upload_to='clubs/', blank=True,
        help_text='Imagen para mostrar en la lista de clubes'
    )

    telegram_group: 'models.CharField[str, str]' = models.CharField(
        'grupo de telegram', max_length=64,
        blank=True, null=True,
    )

    telegram_group_link: 'models.CharField[str, str]' = models.CharField(
        'enlace al grupo de telegram', max_length=64,
        blank=True, null=True,
    )

    managers: 'models.ManyToManyField[None, RelatedManager[AbstractUser]]' = models.ManyToManyField(
        get_user_model(), 'managed_clubs', verbose_name='gestores'
    )

    members: 'models.ManyToManyField[None, RelatedManager[AbstractUser]]' = models.ManyToManyField(
        get_user_model(), 'clubs', verbose_name='miembros'
    )

    _metadata = {
        'title': 'name',
        'description': 'description',
        'image': 'get_image',
    }

    class Meta:
        verbose_name = 'club'
        verbose_name_plural = 'clubes'

        permissions = [
            ('can_link_club', 'Puede vincular un grupo de Telegram con un club')
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('clubs:detail', args=[self.slug])

    def get_image(self) -> str:
        return self.image.url if self.image else static('images/favicon.png')


class ClubMeeting(models.Model):
    """
    Club meeting
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[ClubMeeting]'

    club: 'models.ForeignKey[Club, Club]' = models.ForeignKey(
        Club, models.CASCADE, 'meetings', verbose_name='club'
    )

    title: 'models.CharField[str, str]' = models.CharField(
        'título', max_length=200, blank=True
    )

    place: 'models.CharField[str, str]' = models.CharField(
        'lugar', max_length=120
    )

    moment: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fecha'
    )

    class Meta:
        verbose_name = 'quedada'

        ordering = ['moment']

    def __str__(self) -> str:
        when = self.moment.strftime('%d %b %Y %H:%M')

        return f'{self.club.name} en {self.place} ({when})'
