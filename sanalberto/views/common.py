from django.shortcuts import redirect
from django.views.generic.base import ContextMixin

from meta.views import MetadataMixin

from ..models import Event


class EventMixin(ContextMixin):
    '''Current event mixin'''

    title = 'Inicio'
    description = 'San Alberto: Fiestas patronales de la Facultad de Informática'
    image = 'images/favicon.png'

    check_event_redirect = 'sanalberto:info'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_event = False

    def get_current_event(self):
        if self._current_event is False:
            self._current_event = (
                Event.objects
                    .order_by('-date')
                    .prefetch_related('polls')
                    .first()
                )


        return self._current_event

    def get_context_data(self, **kwargs):
        ev = self.get_current_event()

        if ev:
            self.title = '{} - San Alberto {} - DAFI'.format(
                self.title,
                self._current_event.date.year
            )

        context = super().get_context_data(**kwargs)
        context['event'] = ev
        return context

    def check_event(self, event):
        return True

    def dispatch(self, request, *args, **kwargs):
        event = self.get_current_event()

        if not event or not self.check_event(event):
            return redirect(self.check_event_redirect)

        return super().dispatch(request, *args, **kwargs)
