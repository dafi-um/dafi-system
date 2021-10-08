from typing import (
    TYPE_CHECKING,
    Any,
)

from django.db import models
from django.db.models import F
from django.db.transaction import atomic

from heart.models import Event
from users.models import User


if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class House(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[House]'

    name: 'models.CharField[str, str]' = models.CharField(
        'nombre', max_length=64,
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

    event: 'models.ForeignKey[Event, Event]' = models.ForeignKey(
        Event, models.CASCADE, 'house_points_transactions',
        verbose_name='evento',
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
        verbose_name = 'transacciones de puntos'

        permissions = (
            ('can_give_points', 'Puede dar puntos a una casa'),
        )

    def __str__(self) -> str:
        return f'Transacción #{self.id}'


class HouseProfile(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[HouseProfile]'

    house: 'models.ForeignKey[House, House]' = models.ForeignKey(
        House, models.CASCADE, 'members',
        verbose_name='casa',
    )

    user: 'models.OneToOneField[User, User]' = models.OneToOneField(
        User, models.CASCADE, related_name='house_profile',
        verbose_name='usuario',
    )

    points: 'models.IntegerField[int, int]' = models.IntegerField(
        'puntos',
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

    def _add_points(self, event: Event, points: int) -> 'PointsTransaction | None':
        """Atomically adds points to this profile.

        WARNING: Must be run inside an atomic transaction!!

        Returns `None` if no action was taken.
        """
        transaction = PointsTransaction(
            house=self.house,
            user=self.user,
            points=points,
            event=event,
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

    def check_in(self, event: Event) -> 'PointsTransaction | None':
        """Adds check-in points to this profile from the given event.

        Returns `None` if no action was taken.
        """
        if not event.checkin_points:
            return None

        with atomic():
            return self._add_points(event, event.checkin_points)

    def give_points(self, event: Event, points: int) -> 'PointsTransaction | None':
        """Adds points to this profile from the free points of an event.

        Returns `None` if no action was taken.
        """
        with atomic():
            # If the event has enough points, atomically subtract the
            # specified ones
            updated = (
                Event
                .objects
                .filter(id=event.id, free_points__gte=points)
                .update(points=F('points') - points)
            )

            if not updated:
                # The event doesn't have more points available
                return None

            return self._add_points(event, points)
