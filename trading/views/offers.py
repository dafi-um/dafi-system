from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from bot.notifications import telegram_notify

from heart.models import Year

from ..models import TradeOffer, TradeOfferAnswer, TradeOfferLine

from .common import TradingPeriodMixin


class IndexView(TradingPeriodMixin, ListView):
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['my_answer'] = TradeOffer.objects.filter(
                period=self.get_current_period(), answer__user=self.request.user
            ).exclude(answer=None).first()

            context['my_offer'] = TradeOffer.objects.filter(
                user=self.request.user, period=self.get_current_period()
            ).first()

        return context

    def get_queryset(self):
        user = self.request.user
        query = Q(is_visible=True, answer=None)

        if user.is_authenticated:
            query = query | Q(user=user) | (~Q(answer=None) & Q(answer__user=user))

        return TradeOffer.objects.prefetch_related('lines').filter(Q(period=self.get_current_period()) & query)


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
            context['my_answer'] = self.get_object().answers.filter(user=self.request.user).first()

        if 'answers' not in context:
            context['answers'] = self.get_object().answers.filter(is_visible=True)

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

        if 'description' in request.POST:
            offer.description = request.POST['description']

            if offer.id:
                offer.save()

        if valid:
            if self.is_creation:
                offer.save()
            else:
                answers = TradeOfferAnswer.objects.filter(offer=offer)

                for answer in answers:
                    telegram_notify(answer.user, 'Se ha eliminado tu respuesta a la oferta #{} porque ha sido modificada, deberías revisar la oferta por si todavía te interesa.'.format(offer.id), url=reverse('trading:offer_detail', args=[offer.id]), url_button='Ver oferta')
                    answer.delete()

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
        return reverse('trading:offer_detail', args=[self.get_offer().id])


class TradeOfferEditView(UserPassesTestMixin, TradeOfferEditMixin, DetailView):
    model = TradeOffer

    title = 'Editar una Oferta de Permuta'
    submit_btn = 'Guardar'
    is_creation = False

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
        return reverse('trading:offer_edit', args=[self.get_offer().id])


class TradeOfferDeleteView(UserPassesTestMixin, TradingPeriodMixin, DetailView):
    template_name = 'trading/tradeoffer_delete.html'

    model = TradeOffer

    def test_func(self):
        offer = self.get_object()

        return not offer.answer and self.request.user == offer.user

    def post(self, request, **kwargs):
        offer = self.get_object()

        for answer in offer.answers.all():
            telegram_notify(answer.user, 'Se ha eliminado tu respuesta a la oferta #{} porque ha sido eliminada.'.format(offer.id))
            answer.delete()

        for line in offer.lines.all():
            line.delete()

        offer.delete()

        return redirect('trading:list')

    def get(self, request, *args, **kwargs):
        if self.get_object().answer:
            return redirect(self.get_object())

        return super().get(request, *args, **kwargs)


class ChangeAccessMixin(UserPassesTestMixin):
    def test_func(self):
        offer = self.get_object()
        user = self.request.user

        return offer.answer and (user == offer.user or user == offer.answer.user)


class ChangeProcessView(ChangeAccessMixin, DetailView):
    model = TradeOffer
    template_name = 'trading/change_process.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_completed:
            return self.redirect_success()

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().select_related('answer').prefetch_related('lines')

    def get_lines_data(self):
        data = []
        offer = self.get_object()

        for line in offer.lines.all():
            if offer.user == self.request.user:
                marked = line.get_started_list()
                subjects = line.get_subjects()
            else:
                marked = line.get_completed_list()
                subjects = line.get_started()

            if subjects:
                data.append((line, subjects, marked))

        return data

    def get_context_data(self, **kwargs):
        lines_data = self.get_lines_data()
        completed = True

        if self.request.user == self.get_object().user:
            for line, subjects, _ in self.get_lines_data():
                if line.is_completed:
                    continue
                elif len(line.get_started_list()) != len(subjects):
                    completed = False
                    break
        else:
            completed = False

        context = super().get_context_data(**kwargs)
        context['lines'] = lines_data
        context['completed'] = completed
        return context

    def redirect_success(self):
        return redirect(reverse('trading:change_completed', args=[self.get_object().id]))

    def post(self, request, **kwargs):
        total_completed = 0

        lines_data = self.get_lines_data()

        for line, _, marked in lines_data:
            if line.is_completed:
                total_completed += 1
                continue

            subjects = line.get_subjects_list()

            add = []

            for subject in request.POST.getlist('{}-subjects'.format(line.i)):
                try:
                    subject = int(subject)
                except ValueError:
                    continue

                if subject not in subjects:
                    continue
                elif subject not in marked:
                    add.append(subject)

            if add:
                marked += add
                marked = ','.join(str(x) for x in marked)

                if self.get_object().user == self.request.user:
                    line.started = marked
                else:
                    line.completed = marked

                if len(subjects) == len(line.get_completed_list()):
                    line.is_completed = True
                    total_completed += 1

                line.save()

        if total_completed > 0 and total_completed == len(lines_data):
            offer = self.get_object()
            offer.is_completed = True
            offer.save()

            offer.answer.is_completed = True
            offer.answer.save()

            return self.redirect_success()

        return super().get(request, **kwargs)


class ChangeCompletedView(ChangeAccessMixin, DetailView):
    model = TradeOffer
    template_name = 'trading/change_completed.html'

    def test_func(self):
        return super().test_func() and self.get_object().is_completed
