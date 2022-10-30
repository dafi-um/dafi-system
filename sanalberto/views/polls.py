from collections import Counter
from typing import (
    Any,
    cast,
)

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db import transaction
from django.db.models import (
    Count,
    Q,
)
from django.forms.models import ModelForm
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.http.response import (
    HttpResponseBase,
    HttpResponseRedirectBase,
)
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
)

from meta.views import MetadataMixin

from sanalberto.forms import PollVoteForm
from users.models import User

from ..models import (
    Poll,
    PollDesign,
    PollVote,
)
from .common import EventMixin


class PollMixin(EventMixin):
    """Poll mixin.
    """

    poll: Poll

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        return context

    def get_subtitle(self, context: dict[str, Any]) -> str:
        return self.poll.title

    def check_poll(self, poll: Poll) -> bool:
        # Default method
        return True

    def check_poll_redirect(self, poll: Poll) -> HttpResponseRedirectBase:
        # Default method
        return redirect('sanalberto:index')

    def dispatch(self, request, *args, **kwargs):
        try:
            slug = kwargs.get('slug')
            self.poll = Poll.objects.filter(slug=slug).get()

            assert self.check_poll(self.poll) is True
        except (Poll.DoesNotExist, AssertionError):
            return self.check_poll_redirect(self.poll)

        return super().dispatch(request, *args, **kwargs)


class PollDetailView(EventMixin, MetadataMixin, DetailView):
    """Poll detail view.
    """

    model = Poll

    def get_queryset(self):
        return super().get_queryset().prefetch_related('designs', 'winner__user')

    def get_subtitle(self, context: dict[str, Any]) -> str:
        return cast(Poll, context['object']).title

    def get_context_data(self, **kwargs):
        poll = self.get_object()
        user = self.request.user

        query = Q(is_approved=True)

        if user.is_authenticated:
            query |= Q(user=user)

        designs = poll.designs.filter(query)

        my_designs: list[PollDesign] = []
        approved_designs: list[PollDesign] = []

        for design in designs:
            if user.is_authenticated and design.user == user:
                my_designs.append(design)

            if design.is_approved:
                approved_designs.append(design)

        my_vote: 'PollVote | None' = None

        if user.is_authenticated and poll.voting_enabled:
            my_vote = (
                poll
                .votes
                .filter(user=user)
                .prefetch_related('first', 'second', 'third')
                .first()
            )

        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['approved_designs'] = approved_designs
        context['my_designs'] = my_designs
        context['my_vote'] = my_vote
        return context


class DesignCreateView(PollMixin, MetadataMixin, LoginRequiredMixin, CreateView):
    """Design create view.
    """

    model = PollDesign
    fields = ['title', 'image', 'source_file', 'vector_file']

    def check_poll(self, poll: Poll) -> bool:
        return poll.register_enabled

    def check_poll_redirect(self, poll: Poll) -> HttpResponseRedirectBase:
        return redirect('sanalberto:poll_detail', slug=poll.slug)

    def get_subtitle(self, context: dict[str, Any]) -> str:
        title = cast(Poll, context['object']).title
        return f'Presentar diseño para {title}'

    def form_valid(self, form: 'ModelForm[PollDesign]') -> HttpResponse:
        obj = form.save(commit=False)
        obj.poll = self.poll
        obj.user = cast(User, self.request.user)
        obj.save()

        return redirect('sanalberto:poll_detail', slug=self.poll.slug)


class PollVoteCreateView(
        PollMixin,
        MetadataMixin,
        LoginRequiredMixin,
        UpdateView):
    """Poll vote create view.
    """

    model = PollVote
    form_class = PollVoteForm

    def get_object(self, *args) -> 'PollVote | None':
        return PollVote.objects.filter(user=self.request.user).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['designs'] = self.poll.designs.all()
        return context

    def get_subtitle(self, context: dict[str, Any]) -> str:
        title = cast(Poll, context['object']).title
        return f'Votar diseño para {title}'

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        try:
            initial['first'] = int(self.request.GET['selected'])
        except (ValueError, KeyError):
            pass
        return initial

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['designs'] = self.poll.designs.all()
        return kwargs

    def check_poll(self, poll: Poll) -> bool:
        return poll.voting_enabled

    def check_poll_redirect(self, poll: Poll) -> HttpResponseRedirectBase:
        return redirect('sanalberto:poll_detail', slug=poll.slug)

    def form_valid(self, form: 'ModelForm[PollVote]') -> HttpResponse:
        obj = form.save(commit=False)

        with transaction.atomic():
            existing = (
                PollVote
                .objects
                .filter(user=self.request.user, poll=self.poll)
                .select_for_update()
                .first()
            )

            if existing is None:
                obj.poll = self.poll
                obj.user = cast(User, self.request.user)
                obj.save()
            else:
                existing.first = obj.first
                existing.second = obj.second
                existing.third = obj.third
                existing.save()

        return redirect('sanalberto:poll_detail', slug=obj.poll.slug)

    def dispatch(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponseBase:
        if isinstance(request.user, User) and not request.user.is_verified:
            messages.error(
                request,
                'Debes verificar tu e-mail para poder votar',
                extra_tags='show_profile_btn'
            )
            return redirect('sanalberto:poll_detail', kwargs['slug'])

        return super().dispatch(request, *args, **kwargs)


class PollAdminView(
        PollMixin,
        MetadataMixin,
        UserPassesTestMixin,
        DetailView):

    model = Poll

    template_name_suffix = '_admin'

    def test_func(self) -> 'bool | None':
        user = self.request.user
        return isinstance(user, User) and user.has_perms((
            'sanalberto.view_poll',
            'sanalberto.view_pollvote',
        ))

    def get_subtitle(self, context: dict[str, Any]) -> str:
        title = cast(Poll, context['object']).title
        return f'Administrar encuesta para {title}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        poll: Poll = context['object']
        points: Counter[int] = Counter()

        votes = 0

        if poll.voting_start < timezone.now():
            votes = poll.votes.count()

            for field, multiplier in (('first', 3), ('second', 2), ('third', 1)):
                all_votes = poll.votes.values(field).annotate(count=Count(field))

                for item in all_votes:
                    points[item[field]] += item['count'] * multiplier

        designs = [
            (obj, points.get(obj.id, 0)) for obj in poll.designs.all()
        ]
        designs.sort(key=lambda obj: obj[1], reverse=True)

        context['designs'] = designs
        context['votes'] = votes

        if designs and designs[0][1] > 0:
            context['winner'] = designs[0][0]

        return context
