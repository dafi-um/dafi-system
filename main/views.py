from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from meta.views import MetadataMixin

from blog.models import Post
from clubs.models import ClubMeeting


class IndexView(MetadataMixin, TemplateView):
    template_name = 'main/index.html'

    title = 'DAFI'
    description = 'Delegación de Alumnos de la Facultad de Informática'
    image = 'images/favicon.png'

    def get_context_data(self, **kwargs):
        last_post = Post.objects.all().order_by('-pub_date').first()

        meetings = ClubMeeting.objects.all()
        meetings = meetings.exclude(moment__lt=timezone.now())
        meetings = meetings.order_by('moment')[:5]

        context = super().get_context_data(**kwargs)
        context['last_post'] = last_post
        context['meetings'] = meetings
        return context
