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


class TradeOfferDetailView(DetailView):
    model = TradeOffer


class TradeOfferMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.object.user and not self.object.pending


class TradeOfferAddView(LoginRequiredMixin, CreateView):
    model = TradeOffer
    form_class = TradeOfferForm

    title = 'Agregar oferta'
    submit_btn = 'Crear'

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:tradeoffer_edit', args=[self.object.id])

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TradeOfferEditView(TradeOfferMixin, UpdateView):
    model = TradeOffer
    fields = ['name']

    title = 'Editar oferta'
    submit_btn = 'Guardar'

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:tradeoffer_edit', args=[self.object.id])


class TradeOfferDeleteView(TradeOfferMixin, DeleteView):
    model = TradeOffer

    def get_success_url(self, **kwargs):
        return reverse_lazy('trading:list')
