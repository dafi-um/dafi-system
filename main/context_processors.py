from typing import Any

from django.http import HttpRequest

from .models import MenuEntry


def menu(request: HttpRequest) -> dict[str, Any]:
    return {
        'menu': MenuEntry.objects.all(),
    }
