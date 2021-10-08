from django.urls import path

from . import views


app_name = 'houses'

urlpatterns = [
    path('', views.HousesListView.as_view(), name='list'),
]
