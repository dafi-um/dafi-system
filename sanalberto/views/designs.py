from django.views.generic import ListView

from meta.views import MetadataMixin

from ..models import Design

from .common import EventMixin


class DesignsIndexView(EventMixin, MetadataMixin, ListView):
    '''Designs index view'''

    model = Design

    title = 'Diseños'
