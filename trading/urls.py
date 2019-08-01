from django.urls import path

from . import views

app_name = 'trading'

urlpatterns = [
    path('', views.IndexView.as_view(), name='list'),
    path('crear/', views.DetailView.as_view(), name='tradeoffer_create'),
    path('<int:pk>/aceptar/', views.DetailView.as_view(), name='tradeoffer_accept'),
    path('<int:pk>/editar/', views.DetailView.as_view(), name='tradeoffer_edit'),
    path('<int:pk>/confirmar/', views.DetailView.as_view(), name='tradeoffer_confirm'),
    path('<int:pk>/eliminar/', views.DetailView.as_view(), name='tradeoffer_delete'),
    path('<int:pk>', views.DetailView.as_view(), name='detail'),
]
