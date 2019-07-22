from django.shortcuts import render
from django.views import generic

from .models import Club


class IndexView(generic.ListView):
    def get_queryset(self):
        return Club.objects.all()


class DetailView(generic.DetailView):
    model = Club
