from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView

from heart.models import Year

from ..models import TradeOffer, TradeOfferAnswer, TradeOfferLine

from .common import TradingPeriodMixin


class IndexView(TradingPeriodMixin, ListView):
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['my_offer'] = TradeOffer.objects.filter(
                user=self.request.user, period=self.get_current_period()
            ).first()

        return context

    def get_queryset(self):
        return TradeOffer.objects.prefetch_related('lines').filter(
            period=self.get_current_period(), is_visible=True, answer=None
        )


class TradeOfferDetailView(TradingPeriodMixin, UserPassesTestMixin, DetailView):
    model = TradeOffer

    def test_func(self):
        offer = self.get_object()
        user = self.request.user

        return (
            not offer.answer
            and offer.is_visible
            or user.has_perm('trading.is_manager')
            or offer.user == user
            or offer.answer.user == user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['answer'] = self.get_object().answers.filter(user=self.request.user).first()

        return context

    def get_queryset(self):
        return super().get_queryset().prefetch_related('lines')


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
            if offer.id:
                # TODO: Notify users with answers that this offer was modified and remove their answers (not valid anymore)
                pass
            else:
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
        offer = self.get_object()

        return not offer.answer and self.request.user == offer.user

    def get_queryset(self):
        return super().get_queryset().prefetch_related('lines')

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
        offer = self.get_object()

        return not offer.answer and self.request.user == offer.user

    def post(self, request, **kwargs):
        offer = self.get_object()

        for answer in offer.answers.all():
            # TODO: notify users that this offer was deleted
            answer.delete()

        for line in offer.lines.all():
            line.delete()

        offer.delete()

        return redirect('trading:list')

    def get(self, request, *args, **kwargs):
        if self.get_object().answer:
            return redirect(self.get_object())

        return super().get(request, *args, **kwargs)


class ChangeProcessView(UserPassesTestMixin, DetailView):
    model = TradeOffer
    template_name = 'trading/process.html'

    def test_func(self):
        offer = self.get_object()
        user = self.request.user

        return (
            not offer.is_completed
            and offer.answer
            and (user == offer.user or user == offer.answer.user)
        )

    def get_queryset(self):
        return super().get_queryset().select_related('answer').prefetch_related('lines')
