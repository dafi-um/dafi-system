from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from meta.views import MetadataMixin

from ..models import TradeOffer, TradePeriod


class ManagementListView(PermissionRequiredMixin, MetadataMixin, ListView):
    model = TradeOffer
    template_name = 'trading/management_list.html'

    permission_required = 'trading.is_manager'

    title = 'Gestión de Permutas - DAFI'
    description = 'Sistema de Permutas de la Delegación de Alumnos de la Facultad de Informática'
    image = 'images/favicon.png'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period'] = TradePeriod.get_current()
        return context

    def get_queryset(self):
        return super().get_queryset().prefetch_related('lines')
