from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from ..models import TradeOffer, TradePeriod


class ManagementListView(PermissionRequiredMixin, ListView):
    model = TradeOffer
    template_name = 'trading/management_list.html'

    permission_required = 'trading.is_manager'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period'] = TradePeriod.get_current()
        return context
