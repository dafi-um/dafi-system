from django.urls import path

from . import views

app_name = 'trading'

urlpatterns = [
    path('', views.IndexView.as_view(), name='list'),
    path('crear/', views.TradeOfferAddView.as_view(), name='tradeoffer_create'),
    path('<int:pk>/aceptar/', views.TradeOfferEditView.as_view(), name='tradeoffer_accept'),
    path('<int:pk>/editar/', views.TradeOfferEditView.as_view(), name='tradeoffer_edit'),
    path('<int:pk>/confirmar/', views.TradeOfferEditView.as_view(), name='tradeoffer_confirm'),
    path('<int:pk>/eliminar/', views.TradeOfferDeleteView.as_view(), name='tradeoffer_delete'),
    path('<int:pk>', views.TradeOfferDetailView.as_view(), name='detail'),
]
