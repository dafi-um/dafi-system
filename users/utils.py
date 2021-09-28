from typing import Union

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from .models import User


class SimpleRequest(HttpRequest):

    user: Union[User, AnonymousUser]


class AuthenticatedRequest(HttpRequest):

    user: User
