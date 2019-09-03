from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('crear/', views.SignUpView.as_view(), name='signup'),
]

urls = [
    ('acceder/', 'login', auth_views.LoginView),
    ('salir/', 'logout', auth_views.LogoutView),
    ('cambiar-clave/', 'password_change', auth_views.PasswordChangeView),
    ('cambiar-clave/exito/', 'password_change_done', auth_views.PasswordChangeDoneView),
    ('clave-olvidada/', 'password_reset', auth_views.PasswordResetView),
    ('clave-olvidada/exito/', 'password_reset_done', auth_views.PasswordResetDoneView),
    ('reiniciar-clave/<uidb64>/<token>/', 'password_reset_confirm', auth_views.PasswordResetConfirmView),
    ('reiniciar-clave/exito/', 'password_reset_complete', auth_views.PasswordResetCompleteView),
]

for url, name, view_class in urls:
    view = view_class.as_view(template_name='users/{}.html'.format(name))
    urlpatterns.append(path(url, view, name=name))
