from django.urls import path

from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.IndexView.as_view(), name='list'),
    path('<str:slug>/quedadas/agregar/', views.MeetingAddView.as_view(), name='meeting_add'),
    path('<str:slug>/quedadas/<int:pk>/editar/', views.MeetingEditView.as_view(), name='meeting_edit'),
    path('<str:slug>/quedadas/<int:pk>/eliminar/', views.MeetingDeleteView.as_view(), name='meeting_delete'),
    path('<str:slug>/', views.DetailView.as_view(), name='detail')
]
