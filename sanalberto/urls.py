from django.urls import path

from . import views

app_name = 'sanalberto'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('actividades/', views.ActivitiesIndexView.as_view(), name='activities_index'),
    path('disenos/', views.DesignsIndexView.as_view(), name='designs_index'),
    path('info/', views.InfoView.as_view(), name='info'),
    path('tienda/', views.ShopIndexView.as_view(), name='shop'),
    path('tienda/cerrada/', views.ShopClosedView.as_view(), name='shop_closed'),
]
