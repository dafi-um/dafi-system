from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView, FormView)
from django.views.generic.base import ContextMixin

import requests

from meta.views import MetadataMixin

from main.models import Config
from website.settings import FIUMCRAFT_WHITELIST_ENDPOINT, FIUMCRAFT_WHITELIST_TOKEN

from .models import Committee, DocumentMedia, Group, Meeting, PeopleGroup
from .forms import FiumcraftWhitelistForm


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
            if group.delegate and group.delegate.id not in users_ids:
                users_ids.add(group.delegate.id)

                users_list.append(
                    (str(group.year), group.name, group.delegate)
                )

            if group.subdelegate and group.subdelegate.id not in users_ids:
                users_ids.add(group.subdelegate.id)

                users_list.append(
                    (str(group.year), group.name, group.subdelegate)
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

    def get_queryset(self):
        return super().get_queryset().prefetch_related('year__degree')


class FiumcraftWhitelistView(FormView, MetadataMixin):
    template_name = 'heart/whitelist_form.html'
    form_class = FiumcraftWhitelistForm
    success_url = reverse_lazy('heart:whitelist_fiumcraft_thanks')

    title = 'FIUMCRAFT - WhiteList'
    description = 'Formulario para solicitar acceso al servidor de Minecraft FIUMCRAFT'
    image = 'images/favicon.png'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fiumcraft_url'] = Config.get('fiumcraft_url')
        return context

    def form_valid(self, form):
        nickname = form.cleaned_data['nickname']
        faculty = form.cleaned_data['faculty']
        source = form.cleaned_data['source']
        headers = {
            'Authorization': 'Token ' + FIUMCRAFT_WHITELIST_TOKEN
        }
        params = {
            'nickname': nickname,
            'source': source,
        }
        if faculty:
            params['faculty'] = faculty

        try:
            r = requests.post(
                FIUMCRAFT_WHITELIST_ENDPOINT,
                headers=headers,
                json=params,
                timeout=10
            )
        except requests.exceptions.Timeout:
            return HttpResponseBadRequest('<h1>No se ha obtenido respuesta del servidor.</h1>')

        if r.status_code == 200:
            return super(FiumcraftWhitelistView, self).form_valid(form)

        return HttpResponseBadRequest(
            '<h1>No se ha podido procesar tu solicitud, inténtalo de nuevo más tarde.</h1>'
        )


class FiumcraftWhitelistThanksView(TemplateView, MetadataMixin):
    template_name = "heart/whitelist_form_thanks.html"

    title = 'Gracias por tu solicitud'
    description = 'Gracias por solicitar acceso al servidor de Minecraft FIUMCRAFT'
    image = 'images/favicon.png'
