from django.views.generic import ListView, TemplateView

from meta.views import MetadataMixin

from .models import Group, YEARS_RANGE


class DelegationView(MetadataMixin, TemplateView):
    pass


class StudentsView(MetadataMixin, ListView):
    model = Group
    ordering = ('year', 'name')
    context_object_name = 'groups_all'

    template_name = 'heart/students.html'

    title = 'Los Estudiantes - DAFI'
    description = 'Grupos de Estudiantes y Asambleas de Alumnos de la Facultad de Informática'
    image = 'images/favicon.png'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['years'] = YEARS_RANGE
        return context
