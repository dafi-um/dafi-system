from django.forms import DateTimeInput, ModelForm

from .models import TradeOffer


class TradeOfferForm(ModelForm):
    class Meta:
        model = TradeOffer
        exclude = ['user']
