from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

urlpatterns = [
    path('', include('main.urls')),
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('<path:url>', views.flatpage),
]
