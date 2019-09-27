from django.urls import path

from . import views

app_name = 'heart'

urlpatterns = [
    path('delegacion/', views.DelegationView.as_view(), name='delegation'),
    path('estudiantes/', views.StudentsView.as_view(), name='students'),
]
