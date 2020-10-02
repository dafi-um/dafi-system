from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin

from meta.views import MetadataMixin

from .models import Committee, DocumentMedia, GII, Group, Meeting, PeopleGroup


class AboutUsView(MetadataMixin, TemplateView):
    template_name = 'heart/about_us.html'

    title = 'La Delegación - DAFI'
    description = 'Información sobre la Delegación de Alumnos de la Facultad de Informática'
    image = 'images/favicon.png'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['committees'] = Committee.objects.all()

        context['groups'] = (
            PeopleGroup.objects
            .filter(is_hidden=False)
            .prefetch_related('members')
        )

        return context


class DocumentsView(MetadataMixin, ListView):
    model = DocumentMedia
    ordering = ('name',)

    title = 'Documentos - DAFI'
    description = 'Documentos importantes y archivos relacionados de la Delegación'
    image = 'images/favicon.png'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(hidden=False)
            .order_by('category', 'name')
        )


class MeetingsView(MetadataMixin, ListView):
    model = Meeting
    ordering = ('-date',)

    title = 'Asambleas de Alumnos - DAFI'
    description = 'Convocatorias y Actas de las Asambleas de Alumnos de la Delegación'
    image = 'images/favicon.png'

    def get_queryset(self):
        return super().get_queryset().annotate(Count('documents'))


class MeetingsDetailView(DetailView):
    model = Meeting

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related('attendees')
            .prefetch_related('absents')
            .prefetch_related('documents')
        )

    def get_context_data(self, **kwargs):
        obj = self.get_object()

        context = super().get_context_data(**kwargs)
        context['meta'] = obj.as_meta(self.request)
        context['attendees'] = obj.attendees.order_by('last_name', 'first_name')
        context['absents'] = obj.absents.order_by('last_name', 'first_name')
        return context


class MeetingMixin(ContextMixin):
    model = Meeting

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related('attendees')
            .prefetch_related('absents')
            .prefetch_related('documents')
        )

    def get_context_data(self, **kwargs):
        groups = Group.objects.filter(
            ~Q(delegate=None) | ~Q(subdelegate=None)
        )

        people = (
            PeopleGroup.objects
            .filter(show_in_meetings=True)
            .prefetch_related('members')
        )

        users_list = []
        users_ids = set()

        for group in people:
            for user in group.members.all():
                if user.id in users_ids:
                    continue

                users_list.append(
                    (group.name, None, user)
                )

                users_ids.add(user.id)

        for group in groups:
            if group.course == GII:
                title = 'Año {}'.format(group.year)
            else:
                title = group.get_course_display()

            if group.delegate and group.delegate.id not in users_ids:
                users_ids.add(group.delegate.id)

                users_list.append(
                    (title, group.name, group.delegate)
                )

            if group.subdelegate and group.subdelegate.id not in users_ids:
                users_ids.add(group.subdelegate.id)

                users_list.append(
                    (title, group.name, group.subdelegate)
                )

        context = super().get_context_data(**kwargs)
        context['users'] = users_list
        return context


class MeetingsCreateView(PermissionRequiredMixin, MetadataMixin, MeetingMixin, CreateView):
    model = Meeting
    fields = (
        'date', 'call', 'minutes', 'documents',
        'attendees', 'absents'
    )

    permission_required = 'heart.add_meeting'

    title = 'Crear Asamblea de Alumnos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lists'] = (
            (
                'Asistentes', 'attendees',
                [int(x) for x in self.request.POST.getlist('attendees')]
            ),
            (
                'Ausencias justificadas', 'absents',
                [int(x) for x in self.request.POST.getlist('absents')]
            ),
        )
        context['is_creation'] = True
        return context


class MeetingsUpdateView(PermissionRequiredMixin, MeetingMixin, UpdateView):
    model = Meeting
    fields = (
        'date', 'is_ordinary', 'call', 'minutes', 'minutes_approved',
        'documents', 'attendees', 'absents'
    )

    permission_required = 'heart.add_meeting'

    title = 'Editar Asamblea de Alumnos'

    def get_context_data(self, **kwargs):
        obj = self.get_object()

        context = super().get_context_data(**kwargs)
        context['lists'] = (
            ('Asistentes', 'attendees', obj.attendees.all()),
            ('Ausencias justificadas', 'absents', obj.absents.all()),
        )
        context['meta'] = obj.as_meta(self.request)
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
