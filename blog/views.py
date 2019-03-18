from django.shortcuts import render
from django.views import generic

from .models import Post


class IndexView(generic.ListView):
    def get_queryset(self):
        """Return the last five published posts."""
        return Post.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Post
