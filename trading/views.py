from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import TradeOfferForm
from .models import TradeOffer


class IndexView(ListView):
    def get_queryset(self):
        return TradeOffer.objects.filter(is_answer=False)


class DetailView(DetailView):
    model = TradeOffer
