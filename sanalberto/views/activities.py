from django.utils import timezone
from django.views.generic import ListView, TemplateView

from meta.views import MetadataMixin

from ..models import Activity

from .common import EventMixin


class ActivitiesIndexView(EventMixin, MetadataMixin, ListView):
    '''Activities index view'''

    model = Activity

    title = 'Actividades'
