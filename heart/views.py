from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

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


class MeetingsCreateView(PermissionRequiredMixin, MetadataMixin, CreateView):
    model = Meeting
    fields = ('date', 'call', 'minutes', 'attendees', 'absents')

    permission_required = 'heart.add_meeting'

    title = 'Crear Asamblea de Alumnos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.filter(~Q(delegate=None) | ~Q(subdelegate=None))
        context['attendees'] = self.request.POST.getlist('attendees')
        context['absents'] = self.request.POST.getlist('absents')
        return context


class MeetingsUpdateView(PermissionRequiredMixin, UpdateView):
    model = Meeting
    fields = ('date', 'call', 'minutes', 'attendees', 'absents')

    permission_required = 'heart.add_meeting'

    title = 'Editar Asamblea de Alumnos'

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related('attendees')
            .prefetch_related('absents')
        )

    def get_context_data(self, **kwargs):
        obj = self.get_object()

        context = super().get_context_data(**kwargs)
        context['meta'] = obj.as_meta(self.request)
        context['groups'] = Group.objects.filter(~Q(delegate=None) | ~Q(subdelegate=None))
        context['attendees'] = obj.attendees.all()
        context['absents'] = obj.absents.all()
        return context


class MeetingsDeleteView(PermissionRequiredMixin, MetadataMixin, DeleteView):
    model = Meeting
    permission_required = 'heart.delete_meeting'
    success_url = reverse_lazy('heart:meetings')

    title = 'Eliminar Asamblea de Alumnos'


class StudentsView(MetadataMixin, ListView):
    model = Group

    template_name = 'heart/students.html'

    title = 'Los Estudiantes - DAFI'
    description = 'Grupos de Estudiantes y Asambleas de Alumnos de la Facultad de Informática'
    image = 'images/favicon.png'
