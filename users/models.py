from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


def current_year():
    return datetime.now().year


class User(AbstractUser):
    telegram_user = models.CharField('usuario de telegram', max_length=64, blank=True)
    telegram_id = models.IntegerField('ID de telegram', blank=True, null=True)

    first_year = models.IntegerField('año de ingreso', default=current_year)

    def __str__(self):
        return '{} {} - {}'.format(self.first_name, self.last_name, self.email)
