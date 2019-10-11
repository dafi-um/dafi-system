from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from meta.views import MetadataMixin

from .forms import ClubForm, ClubMeetingForm
from .models import Club, ClubMeeting


class IndexView(MetadataMixin, ListView):
    title = 'Los Clubes de DAFI'
    description = 'Los Clubes de Estudiantes de la Delegación'
    image = 'images/favicon.png'

    def get_queryset(self):
        return Club.objects.order_by('name')


class DetailView(MetadataMixin, DetailView):
    model = Club

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related('managers')
            .prefetch_related('members')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        club = self.get_object()

        context['meta'] = club.as_meta(self.request)
        context['meetings'] = club.meetings.exclude(moment__lt=timezone.now())
        context['members'] = club.members.order_by('first_name', 'last_name')

        if self.request.user.is_authenticated:
            context['is_manager'] = (
                self.request.user.is_superuser
                or self.request.user in club.managers.all()
            )

        return context


class ClubEditView(UserPassesTestMixin, UpdateView):
    model = Club
    form_class = ClubForm

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related('managers')
            .prefetch_related('members')
        )

    def test_func(self):
        user = self.request.user
        managers = self.get_object().managers.all()

        return user and (user.is_superuser or user in managers)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        meta = self.get_object().as_meta(self.request)
        meta.title = 'Editar ' + meta.title

        context['meta'] = meta

        return context


class ClubMeetingMixin(UserPassesTestMixin):
    _club = None

    def get_club(self):
        if not self._club:
            query = Club.objects.filter(slug=self.kwargs['slug'])
            self._club = query.prefetch_related('managers').first()

        return self._club

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['club'] = self.get_club()
        return context

    def test_func(self):
        club = self.get_club()

        return club and (self.request.user.is_superuser or self.request.user in club.managers.all())


class MeetingAddView(ClubMeetingMixin, CreateView):
    model = ClubMeeting
    form_class = ClubMeetingForm

    title = 'Agregar quedada'
    submit_btn = 'Crear'

    def get_success_url(self, **kwargs):
        return reverse_lazy('clubs:meeting_edit', args=[self.kwargs['slug'], self.object.id])

    def form_valid(self, form):
        form.instance.club = self.get_club()
        return super().form_valid(form)


class MeetingEditView(ClubMeetingMixin, UpdateView):
    model = ClubMeeting
    form_class = ClubMeetingForm

    title = 'Editar quedada'
    submit_btn = 'Guardar'

    def get_success_url(self, **kwargs):
        return reverse_lazy('clubs:meeting_edit', args=[self.get_club().slug, self.object.id])


class MeetingDeleteView(ClubMeetingMixin, DeleteView):
    model = ClubMeeting

    def get_success_url(self, **kwargs):
        return reverse_lazy('clubs:detail', args=[self.kwargs['slug']])
