from django.urls import path

from . import views


app_name = 'houses'

urlpatterns = [
    path('', views.HousesListView.as_view(), name='list'),
    path('perfil/<int:pk>/', views.HouseProfileDetailView.as_view(), name='profile'),
    path('algoritmo-seleccionador/', views.SelectorAlgorithmView.as_view(), name='selector'),
]
