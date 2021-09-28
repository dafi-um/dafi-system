from datetime import datetime

from django.contrib.auth.models import (
    AbstractUser,
    Group,
    UserManager,
)
from django.db import models


def current_year() -> int:
    """Gets the current year.
    """
    return datetime.now().year


class User(AbstractUser):
    """Custom user model.
    """

    id: 'models.AutoField[int, int]'

    objects: 'UserManager[User]'

    groups: 'models.manager.RelatedManager[Group]'

    telegram_user: 'models.CharField[str, str]' = models.CharField(
        'usuario de telegram', max_length=64, blank=True
    )
    telegram_id: 'models.IntegerField[int | None, int | None]' = models.IntegerField(
        'ID de telegram', blank=True, null=True
    )

    first_year: 'models.IntegerField[int, int]' = models.IntegerField(
        'año de ingreso', default=current_year
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.email}'
