from django.views.generic import TemplateView

from meta.views import MetadataMixin

from .common import EventMixin


class IndexView(EventMixin, MetadataMixin, TemplateView):
    '''Index event view'''

    template_name = 'sanalberto/index.html'


class InfoView(MetadataMixin, TemplateView):
    '''Information view'''

    title = 'San Alberto - DAFI'
    description = 'San Alberto: Fiestas patronales de la Facultad de Informática'
    image = 'images/favicon.png'

    template_name = 'sanalberto/info.html'
