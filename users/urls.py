from django.urls import path

from . import views

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('crear/', views.SignUpView.as_view(), name='signup'),
]

urls = [
    ('acceder/', 'login', views.LoginView),
    ('salir/', 'logout', views.LogoutView),
    ('cambiar-clave/', 'password_change', views.PasswordChangeView),
    ('cambiar-clave/exito/', 'password_change_done', views.PasswordChangeDoneView),
    ('clave-olvidada/', 'password_reset', views.PasswordResetView),
    ('clave-olvidada/exito/', 'password_reset_done', views.PasswordResetDoneView),
    ('reiniciar-clave/<uidb64>/<token>/', 'password_reset_confirm', views.PasswordResetConfirmView),
    ('reiniciar-clave/exito/', 'password_reset_complete', views.PasswordResetCompleteView),
]

for url, name, view_class in urls:
    view = view_class.as_view(template_name='users/{}.html'.format(name))
    urlpatterns.append(path(url, view, name=name))
