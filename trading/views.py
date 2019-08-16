from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.base import ContextMixin

from heart.models import Year

from .models import TradeOffer, TradeOfferLine, TradePeriod


class TradingPeriodMixin(ContextMixin):
    def __init__(self, *args, **kwargs):
        self._current_period = False
        return super().__init__(*args, **kwargs)

    def get_current_period(self):
        if self._current_period is False:
            self._current_period = TradePeriod.get_current()

        return self._current_period

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period'] = self.get_current_period()
        return context

    def get_template_names(self):
        if not self.get_current_period():
            return ['trading/tradeperiod.html']

        return super().get_template_names()


class IndexView(TradingPeriodMixin, ListView):
    def get_queryset(self):
        return TradeOffer.objects.filter(is_answer=False)


class TradeOfferDetailView(TradingPeriodMixin, DetailView):
    model = TradeOffer


class TradeOfferEditMixin(TradingPeriodMixin):
    template_name = 'trading/tradeoffer_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offer'] = self.get_offer()
        context['lines'] = self.get_lines()
        return context

    def post(self, request, **kwargs):
        valid = []
        deleted = []

        for line in self.get_lines():
            line.curr_group = request.POST.get('{}-curr_group'.format(line.i), 1)
            line.curr_subgroup = request.POST.get('{}-curr_subgroup'.format(line.i), 1)

            line.subjects = ','.join(request.POST.getlist('{}-subjects'.format(line.i)))
            line.wanted_groups = ','.join(request.POST.getlist('{}-wanted_groups'.format(line.i)))

            try:
                line.full_clean(exclude=['offer'])
                valid.append(line)
            except ValidationError as e:
                pass

        if valid:
            offer = self.get_offer()
            offer.save()

            for line in valid:
                line.offer = offer
                line.save()

            return redirect(self.get_success_url(**kwargs))

        return super().get(request, **kwargs)


class TradeOfferAddView(LoginRequiredMixin, TradeOfferEditMixin, TemplateView):
    title = 'Crear una Oferta de Permuta'
    submit_btn = 'Crear Oferta'
    is_creation = True

    def __init__(self, *args, **kwargs):
        self._offer = None
        self._lines = None
        return super().__init__(*args, **kwargs)

    def get_offer(self):
        if not self._offer:
            self._offer = TradeOffer(user=self.request.user, period=self.get_current_period())

        return self._offer

    def get_lines(self):
        if not self._lines:
            self._lines = []

            for year in Year.objects.all():
                self._lines.append(TradeOfferLine(offer=self.get_offer(), year=year))

        return self._lines

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:detail', args=[self.get_offer().id])


class TradeOfferEditView(TradeOfferEditMixin, DetailView):
    model = TradeOffer

    title = 'Editar una Oferta de Permuta'
    submit_btn = 'Guardar'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_offer(self):
        return self.get_object()

    def get_lines(self):
        return self.get_offer().lines.all()

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:tradeoffer_edit', args=[self.get_offer().id])


class TradeOfferDeleteView(TradingPeriodMixin, DetailView):
    template_name = 'trading/tradeoffer_delete.html'

    model = TradeOffer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def post(self, request, **kwargs):
        offer = self.get_object()

        if offer.answer:
            return redirect(offer)

        for line in offer.lines.all():
            line.delete()

        offer.delete()

        return redirect('trading:list')

    def get(self, request, *args, **kwargs):
        if self.get_object().answer:
            return redirect(self.get_object())

        return super().get(request, *args, **kwargs)
