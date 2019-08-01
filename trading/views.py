from django.views.generic import DetailView, ListView

from .models import TradeOffer


class IndexView(ListView):
    def get_queryset(self):
        return TradeOffer.objects.filter(is_answer=False)


class DetailView(DetailView):
    model = TradeOffer
