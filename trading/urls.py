from django.contrib.flatpages import views as flatpages_views
from django.urls import path

from . import views

app_name = 'trading'

urlpatterns = [
    path('', views.IndexView.as_view(), name='list'),
    path('condiciones/', flatpages_views.flatpage, {'url': '/condiciones-permutas/'}, name='conditions'),
    path('crear/', views.TradeOfferAddView.as_view(), name='tradeoffer_create'),
    path('<int:pk>/aceptar/', views.TradeOfferEditView.as_view(), name='tradeoffer_accept'),
    path('<int:pk>/editar/', views.TradeOfferEditView.as_view(), name='tradeoffer_edit'),
    path('<int:pk>/confirmar/', views.TradeOfferEditView.as_view(), name='tradeoffer_confirm'),
    path('<int:pk>/eliminar/', views.TradeOfferDeleteView.as_view(), name='tradeoffer_delete'),
    path('<int:pk>', views.TradeOfferDetailView.as_view(), name='detail'),
]
