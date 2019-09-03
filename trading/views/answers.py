from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, DeleteView
from django.views.generic.base import ContextMixin

from ..models import TradeOffer, TradeOfferAnswer

from .common import TradingPeriodMixin


class TradeOfferAnswerLinesMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        lines = []

        answer = self.get_object()
        groups = answer.get_groups()

        for line in answer.offer.lines.all():
            group, subgroup = groups[str(line.year.id)]

            lines.append((line, {'group': group, 'subgroup': subgroup}))

        context = super().get_context_data(**kwargs)
        context['lines'] = lines
        return context


class TradeOfferAnswerDetailView(UserPassesTestMixin, TradeOfferAnswerLinesMixin, DetailView):
    model = TradeOfferAnswer

    template_name = 'trading/answer_detail.html'

    def test_func(self):
        answer = self.get_object()
        user = self.request.user

        return (
            user.has_perm('trading.is_manager')
            or user == answer.user
            or (answer.is_visible and user == answer.offer.user)
        )

    def get_queryset(self):
        return super().get_queryset().select_related('offer')


class TradeOfferAnswerEditMixin(TradingPeriodMixin):
    def post(self, request, **kwargs):
        offer = self.get_offer()
        answer = self.get_answer()

        data = {}

        for line in offer.lines.all():
            try:
                data[line.year.id] = [
                    int(request.POST.get('{}-group'.format(line.i))),
                    int(request.POST.get('{}-subgroup'.format(line.i))),
                ]
            except TypeError:
                return super().get(request, **kwargs)

        answer.set_groups(data)

        try:
            answer.save()
        except ValidationError:
            return super().get(request, **kwargs)

        return self.on_success(request, **kwargs)


class TradeOfferAnswerCreateView(LoginRequiredMixin, UserPassesTestMixin, TradeOfferAnswerEditMixin, DetailView):
    model = TradeOffer
    template_name = 'trading/answer_form.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._answer = None

    def test_func(self):
        offer = self.get_object()
        user = self.request.user

        if user == offer.user:
            return False

        query = ~Q(offer__answer=None, is_completed=False) | Q(user=user, offer=offer)

        return TradeOfferAnswer.objects.filter(query).count() == 0

    def get_queryset(self):
        return super().get_queryset().prefetch_related('lines')

    def get_offer(self):
        return self.get_object()

    def get_answer(self):
        if not self._answer:
            self._answer = TradeOfferAnswer(offer=self.get_offer(), user=self.request.user)

        return self._answer

    def on_success(self, request, **kwargs):
        return redirect(reverse_lazy('trading:answer_detail', args=[self.get_answer().id]))


class TradeOfferAnswerAccessMixin(UserPassesTestMixin, TradingPeriodMixin):
    def test_func(self):
        answer = self.get_object()

        return self.request.user == answer.user and not answer.offer.answer


class TradeOfferAnswerEditView(TradeOfferAnswerAccessMixin, TradeOfferAnswerLinesMixin, TradeOfferAnswerEditMixin, DetailView):
    model = TradeOfferAnswer
    template_name = 'trading/answer_edit.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('offer__lines')

    def get_offer(self):
        return self.get_object().offer

    def get_answer(self):
        return self.get_object()

    def on_success(self, request, **kwargs):
        messages.success(request, 'Respuesta actualizada correctamente.')
        return super().get(request, **kwargs)


class TradeOfferAnswerDeleteView(TradeOfferAnswerAccessMixin, DeleteView):
    model = TradeOfferAnswer
    template_name = 'trading/answer_delete.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:list')


class TradeOfferAnswerAcceptView(UserPassesTestMixin, TradingPeriodMixin, TradeOfferAnswerLinesMixin, DetailView):
    model = TradeOfferAnswer

    template_name = 'trading/answer_accept.html'

    def test_func(self):
        answer = self.get_object()

        return (
            self.request.user.is_authenticated
            and answer.is_visible
            and self.request.user == answer.offer.user
            and not answer.offer.answer
        )

    def get_queryset(self):
        return super().get_queryset().prefetch_related('offer__lines')

    def post(self, request, **kwargs):
        answer = self.get_object()
        offer = answer.offer

        offer.answer = answer
        offer.is_visible = False
        offer.save()

        query = Q(user=offer.user) | Q(user=answer.user)

        offers = TradeOffer.objects.filter(query & ~Q(pk=offer.id))
        answers = TradeOfferAnswer.objects.filter(query & ~Q(pk=answer.id))

        for offer in offers:
            offer.is_visible = False
            offer.save()

        for answer in answers:
            answer.is_visible = False
            answer.save()

        # TODO: Notify both users that this change process started

        return redirect(reverse_lazy('trading:change_process', args=[offer.id]))
