from django.views.generic.base import ContextMixin

from ..models import TradePeriod


class TradingPeriodMixin(ContextMixin):
    def __init__(self, *args, **kwargs):
        self._current_period = None
        return super().__init__(*args, **kwargs)

    def get_current_period(self):
        if not self._current_period:
            self._current_period = TradePeriod.get_current()

        return self._current_period

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period'] = self.get_current_period()

        if not context['period']:
            context['next_period'] = TradePeriod.get_next()

        return context

    def get_template_names(self):
        if not self.get_current_period() and not self.request.user.has_perm('trading.is_manager'):
            return ['trading/tradeperiod.html']

        return super().get_template_names()
