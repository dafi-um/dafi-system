from django.shortcuts import redirect
from django.views.generic.base import (
    ContextMixin,
    View,
)

from ..models import Event


class EventMixin(ContextMixin, View):
    """Current event mixin.
    """

    _current_event: Event

    title = 'Inicio'
    description = 'San Alberto: Fiestas patronales de la Facultad de Informática'
    image = 'images/favicon.png'

    check_event_redirect = 'sanalberto:info'

    def get_current_event(self) -> Event:
        try:
            return self._current_event
        except AttributeError:
            self._current_event = (
                Event.objects
                .order_by('-date')
                .prefetch_related('polls')
                .get()
            )

            return self._current_event

    def get_context_data(self, **kwargs):
        ev = self.get_current_event()

        self.title = '{} - San Alberto {} - DAFI'.format(
            self.title,
            ev.date.year
        )

        context = super().get_context_data(**kwargs)
        context['event'] = ev
        return context

    def check_event(self, event: Event) -> bool:
        # Default method
        return True

    def dispatch(self, request, *args, **kwargs):
        try:
            event = self.get_current_event()
            assert self.check_event(event)
        except (Event.DoesNotExist, AssertionError):
            return redirect(self.check_event_redirect)

        return super().dispatch(request, *args, **kwargs)
