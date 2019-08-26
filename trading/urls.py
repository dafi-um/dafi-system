from django.contrib.flatpages import views as flatpages_views
from django.urls import path

from . import views

app_name = 'trading'

urlpatterns = [
    path('', views.IndexView.as_view(), name='list'),
    path('condiciones/', flatpages_views.flatpage, {'url': '/condiciones-permutas/'}, name='conditions'),
    path('crear/', views.TradeOfferAddView.as_view(), name='offer_create'),
    path('ofertas/<int:pk>/editar/', views.TradeOfferEditView.as_view(), name='offer_edit'),
    path('ofertas/<int:pk>/eliminar/', views.TradeOfferDeleteView.as_view(), name='offer_delete'),
    path('ofertas/<int:pk>/responder/', views.TradeOfferDetailView.as_view(), name='answer_create'),
    path('ofertas/<int:pk>', views.TradeOfferDetailView.as_view(), name='offer_detail'),
]
