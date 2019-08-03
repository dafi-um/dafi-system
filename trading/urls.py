from django.urls import path

from . import views

app_name = 'trading'

urlpatterns = [
    path('', views.IndexView.as_view(), name='list'),
    path('<int:pk>', views.TradeOfferDetailView.as_view(), name='detail'),
]
