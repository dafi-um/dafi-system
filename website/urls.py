from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path
from django.views import defaults

admin.site.site_header = 'Administración de DAFI'

urlpatterns = [
    path('', include('main.urls')),
    path('blog/', include('blog.urls')),
    path('clubs/', include('clubs.urls')),
    path('permutas/', include('trading.urls')),
    path('cuenta/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('p/<path:url>', views.flatpage),
]

if settings.DEBUG:
    def not_found(request):
        return defaults.page_not_found(request, None)

    urlpatterns.append(path('404/', not_found))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
