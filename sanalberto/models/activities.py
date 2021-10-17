from datetime import (
    datetime,
    timedelta,
)
from typing import (
    TYPE_CHECKING,
    Iterable,
)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    AbstractBaseUser,
    AbstractUser,
    AnonymousUser,
)
from django.db import models
from django.urls.base import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from clubs.models import Club
from heart.models import DocumentMedia

from .event import Event


if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Activity(models.Model):
    """Event activity.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Activity]'

    registrations: 'models.Manager[ActivityRegistration]'

    title: 'models.CharField[str, str]' = models.CharField(
        'título', max_length=120
    )

    description: 'models.TextField[str, str]' = models.TextField(
        'descripción'
    )

    event: 'models.ForeignKey[Event, Event]' = models.ForeignKey(
        Event, models.CASCADE, 'activities',
        verbose_name='evento'
    )

    organiser: 'models.ForeignKey[AbstractUser, AbstractUser]' = models.ForeignKey(
        get_user_model(), models.SET_NULL, blank=True, null=True,
        verbose_name='usuario organizador'
    )

    club: 'models.ForeignKey[Club, Club]' = models.ForeignKey(
        Club, models.CASCADE, blank=True, null=True,
        verbose_name='club organizador'
    )

    start: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'inicio'
    )

    end: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fin'
    )

    is_public: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'mostrar públicamente', default=True
    )

    has_registration: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'necesaria inscripción', default=True
    )

    registration_price: 'models.IntegerField[int, int]' = models.IntegerField(
        'precio de la inscripción', default=100,
        help_text='El precio se debe indicar en céntimos de euro (100 para 1€)'
    )

    image_1: 'models.ImageField' = models.ImageField(
        'imagen 1', upload_to='activities/', null=True, blank=True
    )

    image_2: 'models.ImageField' = models.ImageField(
        'imagen 2', upload_to='activities/', null=True, blank=True
    )

    documents: 'models.ManyToManyField[None, RelatedManager[DocumentMedia]]' = models.ManyToManyField(
        DocumentMedia, blank=True,
        verbose_name='documentos'
    )

    class Meta:
        verbose_name = 'actividad'
        verbose_name_plural = 'actividades'

    def __str__(self) -> str:
        return f'Actividad {self.title}'

    @cached_property
    def get_organisers(self) -> Iterable[AbstractUser]:
        if not self.organiser and not self.club:
            return []

        return [self.organiser] if self.organiser else self.club.managers.all()

    @cached_property
    def accepts_registration(self) -> bool:
        return (
            self.has_registration
            and timezone.now() < self.start + timedelta(minutes=10)
        )

    def get_user_registration(self, user: 'AbstractBaseUser | AnonymousUser') -> 'ActivityRegistration | None':
        if not user.is_authenticated:
            return None

        return self.registrations.filter(user=user).first()


class ActivityRegistration(models.Model):
    """Activity registration.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[ActivityRegistration]'

    activity: 'models.ForeignKey[Activity, Activity]' = models.ForeignKey(
        Activity, models.CASCADE, 'registrations',
        verbose_name='actividad'
    )

    user: 'models.ForeignKey[AbstractUser, AbstractUser]' = models.ForeignKey(
        get_user_model(), models.CASCADE,
        verbose_name='usuario'
    )

    is_paid: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'pagado', default=False
    )

    created: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    comments: 'models.TextField[str | None, str | None]' = models.TextField(
        'comentarios', max_length=500,
        null=True, blank=True
    )

    payment_id: 'models.CharField[str | None, str | None]' = models.CharField(
        'ID de pago', max_length=128,
        null=True, blank=True
    )

    payment_error: 'models.CharField[str | None, str | None]' = models.CharField(
        'error del proceso de pago', max_length=256,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'inscripción'
        verbose_name_plural = 'inscripciones'

    def __str__(self) -> str:
        return f'{self.user} en {self.activity}'

    def get_absolute_url(self) -> str:
        return reverse('sanalberto:registration_detail', args=[self.id])
