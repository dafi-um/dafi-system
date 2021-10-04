from datetime import date as datetime_date
from datetime import (
    datetime,
    timedelta,
)
from decimal import Decimal
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


if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


def date_in_range(start, end):
    now = timezone.now()

    return start <= now and now < end


class Event(models.Model):
    """Year event.

    Groups entities related to a specific year.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Event]'

    activities: 'models.Manager[Activity]'

    polls: 'models.Manager[Poll]'

    date: 'models.DateField[datetime_date, datetime_date]' = models.DateField(
        'fecha'
    )

    selling_start: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'inicio de venta de productos'
    )

    selling_end: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fin de venta de productos'
    )

    def __str__(self) -> str:
        return f'San Alberto de {self.date.year}'

    class Meta:
        verbose_name = 'evento'

    @cached_property
    def shop_enabled(self) -> bool:
        return date_in_range(self.selling_start, self.selling_end)


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


class Poll(models.Model):
    """Designs poll.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Poll]'

    designs: 'models.Manager[PollDesign]'

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

    class Meta:
        verbose_name = 'encuesta'

    def __str__(self) -> str:
        return f'{self.title} ({self.slug})'

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


class Product(models.Model):
    """Shop product.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Product]'

    cost: 'models.DecimalField[Decimal, Decimal]' = models.DecimalField(
        'coste', max_digits=4, decimal_places=2
    )

    price: 'models.DecimalField[Decimal, Decimal]' = models.DecimalField(
        'precio', max_digits=4, decimal_places=2
    )

    stock: 'models.IntegerField[int, int]' = models.IntegerField(
        'stock'
    )

    class Meta:
        verbose_name = 'producto'
