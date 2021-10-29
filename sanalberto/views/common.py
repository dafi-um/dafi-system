from typing import Any

from django.shortcuts import redirect
from django.views.generic.base import (
    ContextMixin,
    View,
)

from ..models import Event


class EventMixin(ContextMixin, View):
    """Current event mixin.
    """

    subtitle = 'Inicio'
    description = 'San Alberto: Fiestas patronales de la Facultad de Informática'
    image = 'images/favicon.png'

    check_event_redirect = 'sanalberto:info'

    event: Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def get_meta_title(self, context: dict[str, Any]) -> str:
        return '{} - San Alberto {} - DAFI'.format(
            self.get_subtitle(context),
            self.event.date.year
        )

    def get_subtitle(self, context: dict[str, Any]) -> str:
        return self.subtitle

    def check_event(self, event: Event) -> bool:
        # Default method
        return True

    def dispatch(self, request, *args, **kwargs):
        try:
            event = (
                Event.objects
                .order_by('-date')
                .prefetch_related('polls')
                .first()
            )
            assert event is not None
            assert self.check_event(event)
        except AssertionError:
            return redirect(self.check_event_redirect)

        self.event = event

        return super().dispatch(request, *args, **kwargs)
