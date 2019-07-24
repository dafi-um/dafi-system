from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

admin.site.site_header = 'Administración de DAFI'

urlpatterns = [
    path('', include('main.urls')),
    path('blog/', include('blog.urls')),
    path('clubs/', include('clubs.urls')),
    path('cuenta/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('p/<path:url>', views.flatpage),
]
