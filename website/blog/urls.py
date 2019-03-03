from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='list'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail')
]
