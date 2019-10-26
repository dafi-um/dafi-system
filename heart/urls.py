from django.urls import path

from . import views

app_name = 'heart'

urlpatterns = [
    path('asambleas/', views.MeetingsView.as_view(), name='meetings'),
    path('asambleas/crear/', views.MeetingsCreateView.as_view(), name='meetings_create'),
    path('asambleas/eliminar/<int:pk>/', views.MeetingsDeleteView.as_view(), name='meetings_delete'),
    path('asambleas/<int:pk>/', views.MeetingsUpdateView.as_view(), name='meetings_update'),
    path('documentos/', views.DocumentsView.as_view(), name='docs'),
    path('estudiantes/', views.StudentsView.as_view(), name='students'),
]
