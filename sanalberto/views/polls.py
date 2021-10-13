from typing import (
    Any,
    cast,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.db.models import Q
from django.forms.models import ModelForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
)

from meta.views import MetadataMixin

from sanalberto.forms import PollVoteForm

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

    def check_poll(self, poll: Poll) -> bool:
        # Default method
        return True

    def dispatch(self, request, *args, **kwargs):
        try:
            slug = kwargs.get('slug')
            self.poll = Poll.objects.filter(slug=slug).get()

            assert self.check_poll(self.poll) is True
        except (Poll.DoesNotExist, AssertionError):
            return redirect('sanalberto:index')

        self.title = self.poll.title

        return super().dispatch(request, *args, **kwargs)


class PollDetailView(EventMixin, MetadataMixin, DetailView):
    """Poll detail view.
    """

    model = Poll

    def get_queryset(self):
        return super().get_queryset().prefetch_related('designs')

    def get_object(self, queryset=None) -> Poll:
        obj: Poll = super().get_object(queryset=queryset)
        self.title = obj.title
        return obj

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
        voted_designs: set[PollDesign] = set()

        if user.is_authenticated and poll.voting_enabled:
            my_vote = (
                poll
                .votes
                .filter(user=user)
                .prefetch_related('first', 'second', 'third')
                .first()
            )

            if my_vote is not None:
                voted_designs.update([
                    my_vote.first,
                    my_vote.second,
                    my_vote.third,
                ])

        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['approved_designs'] = approved_designs
        context['my_designs'] = my_designs
        context['my_vote'] = my_vote
        context['voted_designs'] = voted_designs
        return context


class DesignCreateView(PollMixin, MetadataMixin, LoginRequiredMixin, CreateView):
    """Design create view.
    """

    model = PollDesign
    fields = ['title', 'image', 'source_file', 'vector_file']

    def check_poll(self, poll: Poll) -> bool:
        return poll.register_enabled

    def form_valid(self, form: 'ModelForm[PollDesign]') -> HttpResponse:
        obj = form.save(commit=False)
        obj.poll = self.poll
        obj.user = cast(AbstractUser, self.request.user)
        obj.save()

        return redirect('sanalberto:poll_detail', slug=obj.poll.slug)


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
                obj.user = cast(AbstractUser, self.request.user)
                obj.save()
            else:
                existing.first = obj.first
                existing.second = obj.second
                existing.third = obj.third
                existing.save()

        return redirect('sanalberto:poll_detail', slug=obj.poll.slug)
