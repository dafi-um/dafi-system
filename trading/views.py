from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import TradeOfferForm
from .models import TradeOffer, TradePeriod


class TradingPeriodMixin(ContextMixin):
    def __init__(self, *args, **kwargs):
        self._current_period = False
        return super().__init__(*args, **kwargs)

    def _get_current_period(self):
        if self._current_period is False:
            self._current_period = TradePeriod.get_current()

        return self._current_period

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period'] = self._get_current_period()
        return context

    def get_template_names(self):
        if not self._get_current_period():
            return ['trading/tradeperiod.html']

        return super().get_template_names()


class IndexView(TradingPeriodMixin, ListView):
    def get_queryset(self):
        return TradeOffer.objects.filter(is_answer=False)


class TradeOfferDetailView(TradingPeriodMixin, DetailView):
    model = TradeOffer


class TradeOfferMixin(TradingPeriodMixin, UserPassesTestMixin):
    def test_func(self):
        return not self.object.answer and self.request.user == self.object.user


class TradeOfferAddView(TradingPeriodMixin, LoginRequiredMixin, CreateView):
    model = TradeOffer
    form_class = TradeOfferForm

    title = 'Agregar oferta'
    submit_btn = 'Crear'

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:tradeoffer_edit', args=[self.object.id])

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['years'] = range(1, 5)
        return context


class TradeOfferEditView(TradeOfferMixin, UpdateView):
    model = TradeOffer
    fields = ['name']

    title = 'Editar oferta'
    submit_btn = 'Guardar'

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:tradeoffer_edit', args=[self.object.id])


class TradeOfferDeleteView(TradeOfferMixin, DeleteView):
    model = TradeOffer

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:list')
