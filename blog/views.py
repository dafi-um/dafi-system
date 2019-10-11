from django.shortcuts import render
from django.views.generic import DetailView, ListView

from meta.views import MetadataMixin

from .models import Post


class IndexView(MetadataMixin, ListView):
    title = 'El blog de DAFI'
    description = 'Noticias de la Delegación de Estudiantes de Informática'
    image = 'images/favicon.png'

    def get_queryset(self):
        """Return the last five published posts."""
        return Post.objects.order_by('-pub_date')[:5]


class DetailView(MetadataMixin, DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context
