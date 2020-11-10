from django.views.generic import DetailView, ListView, TemplateView

from meta.views import Meta, MetadataMixin

from ..models import Activity

from .common import EventMixin


class ActivitiesIndexView(EventMixin, MetadataMixin, TemplateView):
    '''Activities index view'''

    template_name = 'sanalberto/activity_list.html'

    title = 'Actividades'

    def get_context_data(self, **kwargs):
        event = self.get_current_event()

        activities = Activity.objects.filter(event=event).order_by('start')

        context = super().get_context_data(**kwargs)
        context['activities'] = activities
        return context


class ActivityDetailView(EventMixin, MetadataMixin, DetailView):
    '''Activity detail view'''

    model = Activity

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj:
            self.title = obj.title

        return obj
