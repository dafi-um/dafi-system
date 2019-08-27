from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.base import ContextMixin

from heart.models import Year

from .models import TradeOffer, TradeOfferAnswer, TradeOfferLine, TradePeriod


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

    def filter_query(self):
        query = Q(is_visible=True) & Q(answer=None)

        if self.request.user.is_authenticated:
            query = query | Q(user=self.request.user) | Q(answer__user=self.request.user)

        return Q(period=self.get_current_period()) & query


class IndexView(TradingPeriodMixin, ListView):
    paginate_by = 10

    def get_queryset(self):
        return TradeOffer.objects.filter(self.filter_query())


class TradeOfferDetailView(TradingPeriodMixin, DetailView):
    model = TradeOffer

    def get_queryset(self):
        return super().get_queryset().filter(self.filter_query())

class TradeOfferEditMixin(TradingPeriodMixin):
    template_name = 'trading/tradeoffer_form.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._errors = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offer'] = self.get_offer()
        context['lines'] = self.get_lines()
        context['errors'] = self._errors
        return context

    def post(self, request, **kwargs):
        valid = []

        deleted = 0

        for line in self.get_lines():
            line.curr_group = request.POST.get('{}-curr_group'.format(line.i), 1)
            line.curr_subgroup = request.POST.get('{}-curr_subgroup'.format(line.i), 1)

            line.subjects = ','.join(request.POST.getlist('{}-subjects'.format(line.i)))
            line.wanted_groups = ','.join(request.POST.getlist('{}-wanted_groups'.format(line.i)))

            try:
                line.full_clean(exclude=['offer'])
                valid.append(line)
            except ValidationError as e:
                if line.get_subjects_list():
                    self._errors.append(e)
                elif line.id:
                    line.delete()
                    deleted += 1

        offer = self.get_offer()

        if valid:
            if not offer.id:
                offer.save()

            for line in valid:
                line.offer = offer
                line.save()

            return redirect(self.get_success_url(**kwargs))
        elif deleted:
            offer.delete()

            return redirect('trading:list')

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
        return reverse_lazy('trading:offer_detail', args=[self.get_offer().id])


class TradeOfferEditView(UserPassesTestMixin, TradeOfferEditMixin, DetailView):
    model = TradeOffer

    title = 'Editar una Oferta de Permuta'
    submit_btn = 'Guardar'

    def __init__(self, *args, **kwargs):
        self._lines = None
        return super().__init__(*args, **kwargs)

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_queryset(self):
        return super().get_queryset().filter(answer=None)

    def get_offer(self):
        return self.get_object()

    def get_lines(self):
        if not self._lines:
            self._lines = []

            lines = {x.year.id: x for x in self.get_offer().lines.all()}

            for year in Year.objects.all():
                if year.id in lines:
                    self._lines.append(lines[year.id])
                else:
                    self._lines.append(TradeOfferLine(offer=self.get_offer(), year=year))

        return self._lines

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:offer_edit', args=[self.get_offer().id])


class TradeOfferDeleteView(UserPassesTestMixin, TradingPeriodMixin, DetailView):
    template_name = 'trading/tradeoffer_delete.html'

    model = TradeOffer

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_queryset(self):
        return super().get_queryset().filter(answer=None)

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


class TradeOfferAnswerCreate(UserPassesTestMixin, TradingPeriodMixin, DetailView):
    model = TradeOffer
    template_name = 'trading/answer_form.html'

    def test_func(self):
        return self.request.user != self.get_object().user

    def post(self, request, **kwargs):
        offer = self.get_object()
        answer = TradeOfferAnswer(offer=offer, user=request.user)

        data = {}

        for line in offer.lines.all():
            try:
                data[line.year.id] = [
                    int(request.POST.get('{}-group'.format(line.i))),
                    int(request.POST.get('{}-subgroup'.format(line.i))),
                ]
            except ValueError:
                return super().get(request, **kwargs)

        answer.set_groups(data)

        try:
            answer.save()
            return redirect(reverse_lazy('trading:answer_detail', args=[answer.id]))
        except ValidationError:
            pass

        return super().get(request, **kwargs)

