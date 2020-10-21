from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView

from meta.views import MetadataMixin

from ..models import Design

from .common import EventMixin


class RegisterMixin(EventMixin):
    '''Design register mixin'''

    title = 'Diseños'

    check_event_redirect = 'sanalberto:designs_index'

    def check_event(self, event):
        return event.design_register_enabled


class DesignsIndexView(EventMixin, MetadataMixin, ListView):
    '''Designs index view'''

    model = Design

    title = 'Diseños'


class DesignCreateView(RegisterMixin, MetadataMixin, LoginRequiredMixin, CreateView):
    '''Design create view'''

    model = Design
    fields = ['title', 'image', 'source_file']

    title = 'Presentar diseño'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.event = self.get_current_event()
        obj.user = self.request.user
        obj.save()

        return redirect('sanalberto:designs_index')
