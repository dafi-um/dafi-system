from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ClubMeetingForm
from .models import Club, ClubMeeting


class IndexView(ListView):
    def get_queryset(self):
        return Club.objects.all()


class DetailView(DetailView):
    model = Club


class ClubMeetingMixin(UserPassesTestMixin):
    _club = None

    def get_club(self):
        if not self._club:
            self._club = Club.objects.filter(slug=self.kwargs['slug']).first()

        return self._club

    def test_func(self):
        club = self.get_club()

        return club and self.request.user == club.manager


class MeetingAddView(ClubMeetingMixin, CreateView):
    model = ClubMeeting
    form_class = ClubMeetingForm

    title = 'Agregar quedada'
    submit_btn = 'Crear'

    def form_valid(self, form):
        meeting = form.save(commit=False)
        meeting.club = self.get_club()
        meeting.save()
        return HttpResponseRedirect(reverse('clubs:meeting_edit', args=[self.kwargs['slug'], meeting.id]))


class MeetingEditView(ClubMeetingMixin, UpdateView):
    model = ClubMeeting
    form_class = ClubMeetingForm

    title = 'Editar quedada'
    submit_btn = 'Guardar'

    def get_success_url(self, **kwargs):
        return reverse_lazy('clubs:meeting_edit', args=[self.get_club().slug, self.object.id])


class MeetingDeleteView(ClubMeetingMixin, DeleteView):
    model = ClubMeeting
    success_url = reverse_lazy('clubs:list')
