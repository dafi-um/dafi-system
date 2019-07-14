from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def current_year():
    return datetime.now().year


class User(AbstractUser):
    telegramUser = models.CharField(_('telegram username'), max_length=64, blank=True)
    telegramId = models.CharField(_('telegram ID'), max_length=64, blank=True)

    firstYear = models.IntegerField(_('first year'), default=current_year)
