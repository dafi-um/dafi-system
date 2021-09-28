from django.utils import timezone
from django.views.generic import (
    ListView,
    TemplateView,
)

from meta.views import MetadataMixin

from sanalberto.models import Event

from .common import EventMixin


class ShopMixin(EventMixin):
    """Shop mixin.
    """

    title = 'Tienda'

    check_event_redirect = 'sanalberto:shop_closed'

    def check_event(self, event: Event) -> bool:
        return event.shop_enabled


class ShopIndexView(ShopMixin, MetadataMixin, ListView):
    """Shop index view.
    """

    pass


class ShopClosedView(EventMixin, MetadataMixin, TemplateView):
    """Shop closed alert view.
    """

    template_name = 'sanalberto/shop_closed.html'

    title = 'Tienda cerrada'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['soon'] = self.get_current_event().selling_start > timezone.now()
        return context
