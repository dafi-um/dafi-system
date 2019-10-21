from django.urls import path

from . import views

app_name = 'heart'

urlpatterns = [
    path('asambleas/', views.MeetingsView.as_view(), name='meetings'),
    path('documentos/', views.DocumentsView.as_view(), name='docs'),
    path('estudiantes/', views.StudentsView.as_view(), name='students'),
]
