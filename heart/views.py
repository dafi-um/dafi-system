from django.views.generic import ListView

from meta.views import MetadataMixin

from .models import DocumentMedia, Group, Meeting, YEARS_RANGE


class DocumentsView(MetadataMixin, ListView):
    model = DocumentMedia
    ordering = ('name',)

    title = 'Documentos - DAFI'
    description = 'Documentos importantes y archivos relacionados de la Delegación'
    image = 'images/favicon.png'

    def get_queryset(self):
        return super().get_queryset().filter(hidden=False)


class MeetingsView(MetadataMixin, ListView):
    model = Meeting
    ordering = ('-date',)

    title = 'Asambleas de Alumnos - DAFI'
    description = 'Convocatorias y Actas de las Asambleas de Alumnos de la Delegación'
    image = 'images/favicon.png'


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
