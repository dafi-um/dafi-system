from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import CreateView, DetailView, TemplateView
from django.views.generic.base import ContextMixin

from meta.views import MetadataMixin

from ..models import Poll, PollDesign

from .common import EventMixin


class PollMixin(EventMixin):
    '''Poll mixin'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._poll = False

    def get_poll(self):
        if self._poll is False:
            slug = self.kwargs.get('slug')
            self._poll = Poll.objects.filter(slug=slug).first()

            if self._poll:
                self.title = self._poll.title

        return self._poll

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poll'] = self.get_poll()
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.get_poll():
            return redirect('sanalberto:index')

        return super().dispatch(request, *args, **kwargs)


class PollIndexView(EventMixin, MetadataMixin, DetailView):
    '''Poll index view'''

    model = Poll

    def get_queryset(self):
        return super().get_queryset().prefetch_related('designs')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj:
            self.title = obj.title

        return obj

    def get_my_designs(self):
        if not self.request.user.is_authenticated:
            return None

        return self.get_object().designs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['my_designs'] = self.get_my_designs()
        return context


class DesignCreateView(PollMixin, MetadataMixin, LoginRequiredMixin, CreateView):
    '''Design create view'''

    model = PollDesign
    fields = ['title', 'image', 'source_file', 'vector_file']

    def dispatch(self, request, *args, **kwargs):
        poll = self.get_poll()

        if not poll or not poll.register_enabled:
            return redirect('sanalberto:index')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.poll = self.get_poll()
        obj.user = self.request.user
        obj.save()

        return redirect('sanalberto:poll_index', slug=obj.poll.slug)
