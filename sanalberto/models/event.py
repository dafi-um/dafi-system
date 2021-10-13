from datetime import date as datetime_date
from datetime import datetime
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property


if TYPE_CHECKING:
    from .activities import Activity
    from .polls import Poll


def date_in_range(start: datetime, end: datetime):
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
