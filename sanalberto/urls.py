from django.urls import path

from . import views

app_name = 'sanalberto'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('actividades/', views.ActivitiesIndexView.as_view(), name='activities_index'),
    path('actividades/<int:pk>/', views.ActivityDetailView.as_view(), name='activity_detail'),
    path('actividades/<int:pk>/inscripcion/', views.ActivityRegisterView.as_view(), name='activity_register'),
    path('actividades/<int:pk>/inscripciones/', views.ActivityRegistrationsView.as_view(), name='activity_registrations'),
    path('inscripciones/', views.RegistrationListView.as_view(), name='registration_list'),
    path('inscripciones/<int:pk>/', views.RegistrationDetailView.as_view(), name='registration_detail'),
    path('inscripciones/<int:pk>/pagado/', views.RegistrationPaidView.as_view(), name='registration_paid'),
    path('info/', views.InfoView.as_view(), name='info'),
    path('tienda/', views.ShopIndexView.as_view(), name='shop'),
    path('tienda/cerrada/', views.ShopClosedView.as_view(), name='shop_closed'),
    path('<str:slug>/', views.PollIndexView.as_view(), name='poll_index'),
    path('<str:slug>/registrar/', views.DesignCreateView.as_view(), name='design_create'),
]
