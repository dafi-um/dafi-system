from datetime import datetime
from functools import partial
from os import path
from typing import (
    TYPE_CHECKING,
    Any,
)

from django.db import models
from django.db.models import F
from django.db.transaction import atomic

from heart.models import Activity
from users.models import User


if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


def house_logo_path(base: str, instance: 'House', filename: str) -> str:
    """Generates a path for a house logo.
    """
    ext = path.splitext(filename)[1] or '.png'
    return f'{base}/{instance.id}{ext}'


class House(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[House]'

    name: 'models.CharField[str, str]' = models.CharField(
        'nombre', max_length=64,
    )

    logo: 'models.ImageField' = models.ImageField(
        'logo', upload_to=partial(house_logo_path, 'houses/logos/'),
    )

    plain_logo: 'models.ImageField' = models.ImageField(
        'logo plano', upload_to=partial(house_logo_path, 'houses/plain-logos/'),
        help_text='Se utilizará como fondo en los perfiles',
    )

    points: 'models.PositiveIntegerField[int, int]' = models.PositiveIntegerField(
        'puntos', default=0,
    )

    managers: 'models.ManyToManyField[None, RelatedManager[User]]' = models.ManyToManyField(
        User, 'house_managers',
        verbose_name='gestores',
    )

    default_rank: 'models.CharField[str, str]' = models.CharField(
        'rango para nuevos miembros', max_length=64,
    )

    class Meta:
        verbose_name = 'casa'

    def __str__(self) -> str:
        return f'Casa #{self.id}: {self.name}'


class PointsTransaction(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[PointsTransaction]'

    house: 'models.ForeignKey[House, House]' = models.ForeignKey(
        House, models.CASCADE, 'transactions',
        verbose_name='casa',
    )

    activity: 'models.ForeignKey[Activity, Activity]' = models.ForeignKey(
        Activity, models.CASCADE, 'house_points_transactions',
        verbose_name='actividad',
    )

    user: 'models.ForeignKey[User | None, User | None]' = models.ForeignKey(
        User, models.CASCADE, 'house_points',
        blank=True, null=True,
        verbose_name='usuario',
    )

    points: 'models.IntegerField[int, int]' = models.IntegerField(
        'puntos',
    )

    class Meta:
        verbose_name = 'transacción de puntos'
        verbose_name_plural = 'transacciones de puntos'

        permissions = (
            ('can_give_points', 'Puede dar puntos a una casa'),
        )

    def __str__(self) -> str:
        return f'Transacción #{self.id}'


class HouseProfile(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[HouseProfile]'

    user: 'models.OneToOneField[User, User]' = models.OneToOneField(
        User, models.CASCADE, related_name='house_profile',
        verbose_name='usuario',
    )

    house: 'models.ForeignKey[House, House]' = models.ForeignKey(
        House, models.CASCADE, related_name='members',
        verbose_name='casa',
    )

    points: 'models.IntegerField[int, int]' = models.IntegerField(
        'puntos', default=0,
    )

    rank: 'models.CharField[str, str]' = models.CharField(
        'rango', max_length=64,
    )

    nickname: 'models.CharField[str, str]' = models.CharField(
        'apodo', max_length=64, blank=True, default='',
    )

    class Meta:
        verbose_name = 'perfil de casa'
        verbose_name_plural = 'perfiles de casa'

    def __str__(self) -> str:
        return f'Perfil de Casa #{self.id}: {self.user} en {self.house}'

    @property
    def display_name(self) -> str:
        """Gets the display name for this profile user.
        """
        return self.nickname or self.user.display_name

    def _add_points(self, activity: Activity, points: int) -> 'PointsTransaction | None':
        """Atomically adds points to this profile.

        WARNING: Must be run inside an atomic transaction!!

        Returns `None` if no action was taken.
        """
        transaction = PointsTransaction(
            house=self.house,
            user=self.user,
            points=points,
            activity=activity,
        )

        # Type the F-expression as Any to avoid typing issues
        new_points: Any = F('points') + points

        # Update atomically using F-expressions and refresh to get
        # the updated value and remove the F-expression assignment
        self.points = new_points
        self.save(update_fields=('points',))
        self.refresh_from_db()

        self.house.points = new_points
        self.house.save(update_fields=('points',))
        self.house.refresh_from_db()

        # Save the points transaction inside a DB transaction to try
        # to be "atomic"
        transaction.save()

        return transaction

    def check_in(self, activity: Activity) -> 'PointsTransaction | None':
        """Adds check-in points to this profile from the given activity.

        Returns `None` if no action was taken.
        """
        if not activity.checkin_points:
            return None

        with atomic():
            return self._add_points(activity, activity.checkin_points)

    def give_points(self, activity: Activity, points: int) -> 'PointsTransaction | None':
        """Adds points to this profile from the free points of an activity.

        Returns `None` if no action was taken.
        """
        with atomic():
            # If the activity has enough points, atomically subtract the
            # specified ones
            updated = (
                Activity
                .objects
                .filter(id=activity.id, free_points__gte=points)
                .update(points=F('points') - points)
            )

            if not updated:
                # The activity doesn't have more points available
                return None

            return self._add_points(activity, points)


class SelectorQuestion(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[SelectorQuestion]'

    options: 'models.Manager[SelectorOption]'

    question: 'models.TextField[str, str]' = models.TextField(
        'pregunta',
    )

    category: 'models.CharField[str, str]' = models.CharField(
        'categoría', max_length=120,
    )

    class Meta:
        verbose_name = 'pregunta del seleccionador'
        verbose_name_plural = 'preguntas del seleccionador'

    def __str__(self) -> str:
        return f'Pregunta #{self.id} - {self.question}'


class SelectorOption(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[SelectorOption]'

    points: 'models.Manager[SelectorOptionPoints]'

    question: 'models.ForeignKey[SelectorQuestion, SelectorQuestion]' = models.ForeignKey(
        SelectorQuestion, models.CASCADE, related_name='options',
        verbose_name='pregunta',
    )

    text: 'models.CharField[str, str]' = models.CharField(
        'respuesta', max_length=300,
    )

    class Meta:
        verbose_name = 'opción de pregunta'
        verbose_name_plural = 'opciones de pregunta'

    def __str__(self) -> str:
        return f'Opción #{self.id}'


class SelectorOptionPoints(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[SelectorOptionPoints]'

    option: 'models.ForeignKey[SelectorOption, SelectorOption]' = models.ForeignKey(
        SelectorOption, models.CASCADE, related_name='points',
        verbose_name='opción',
    )

    house: 'models.ForeignKey[House, House]' = models.ForeignKey(
        House, models.CASCADE, related_name='options_points',
        verbose_name='casa',
    )

    points: 'models.IntegerField' = models.IntegerField(
        'puntos',
    )

    class Meta:
        verbose_name = 'puntos de opción'
        verbose_name_plural = 'puntos de opción'

    def __str__(self) -> str:
        return f'Puntos #{self.id}'


class SelectorResult(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[SelectorResult]'

    points: 'models.Manager[SelectorResultPoints]'

    user: 'models.OneToOneField[User, User]' = models.OneToOneField(
        User, models.CASCADE, related_name='selector_result',
        verbose_name='usuario',
    )

    created: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'resultado del seleccionador'
        verbose_name_plural = 'resultados del seleccionador'

    def __str__(self) -> str:
        return f'Resultado #{self.id}'


class SelectorResultPoints(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[SelectorResultPoints]'

    result: 'models.ForeignKey[SelectorResult, SelectorResult]' = models.ForeignKey(
        SelectorResult, models.CASCADE, related_name='points',
        verbose_name='resultado',
    )

    house: 'models.ForeignKey[House, House]' = models.ForeignKey(
        House, models.CASCADE,
        verbose_name='casa',
    )

    points: 'models.IntegerField' = models.IntegerField(
        'puntos',
    )

    class Meta:
        verbose_name = 'puntos de resultado'
        verbose_name_plural = 'puntos de resultado'

    def __str__(self) -> str:
        return f'Puntos #{self.id}'
