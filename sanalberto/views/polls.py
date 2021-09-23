from typing import (
    Iterable,
    cast,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.forms.models import ModelForm
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
)

from meta.views import MetadataMixin

from ..models import (
    Poll,
    PollDesign,
)
from .common import EventMixin


class PollMixin(EventMixin):
    """Poll mixin.
    """

    _poll: Poll

    def get_poll(self) -> Poll:
        try:
            return self._poll
        except AttributeError:
            slug = self.kwargs.get('slug')
            self._poll = Poll.objects.filter(slug=slug).get()
            self.title = self._poll.title

        return self._poll

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poll'] = self.get_poll()
        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            self.get_poll()
        except Poll.DoesNotExist:
            return redirect('sanalberto:index')

        return super().dispatch(request, *args, **kwargs)


class PollIndexView(EventMixin, MetadataMixin, DetailView):
    """Poll index view.
    """

    model = Poll

    def get_queryset(self):
        return super().get_queryset().prefetch_related('designs')

    def get_object(self, queryset=None) -> Poll:
        obj: Poll = super().get_object(queryset=queryset)
        self.title = obj.title
        return obj

    def get_my_designs(self) -> 'Iterable[PollDesign] | None':
        if not self.request.user.is_authenticated:
            return None

        return self.get_object().designs.filter(user=self.request.user)

    def get_approved_designs(self) -> Iterable[PollDesign]:
        return self.get_object().designs.filter(is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['approved_designs'] = self.get_approved_designs()
        context['my_designs'] = self.get_my_designs()
        return context


class DesignCreateView(PollMixin, MetadataMixin, LoginRequiredMixin, CreateView):
    """Design create view.
    """

    model = PollDesign
    fields = ['title', 'image', 'source_file', 'vector_file']

    def dispatch(self, request, *args, **kwargs):
        try:
            poll = self.get_poll()
            assert poll.register_enabled
        except (Poll.DoesNotExist, AssertionError):
            return redirect('sanalberto:index')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: 'ModelForm[PollDesign]') -> HttpResponse:
        obj = form.save(commit=False)
        obj.poll = self.get_poll()
        obj.user = cast(AbstractUser, self.request.user)
        obj.save()

        return redirect('sanalberto:poll_index', slug=obj.poll.slug)
