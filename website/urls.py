from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

urlpatterns = [
    path('', include('main.urls')),
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('p/<path:url>', views.flatpage),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
