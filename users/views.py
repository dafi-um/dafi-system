from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from meta.views import MetadataMixin

from .forms import (
    ProfileTelegramForm,
    ProfileUserForm,
    SignUpForm,
)
from .models import User
from .utils import AuthenticatedRequest


class ProfileView(LoginRequiredMixin, MetadataMixin, TemplateView):

    request: AuthenticatedRequest

    template_name = 'users/profile.html'

    title = 'Mi Perfil - DAFI'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = ProfileUserForm(instance=self.request.user)
        context['telegram_form'] = ProfileTelegramForm(instance=self.request.user)
        return context

    def post(self, request: AuthenticatedRequest, **kwargs) -> HttpResponse:
        success = False

        if 'profile_form' in request.POST:
            form = ProfileUserForm(request.POST, instance=request.user)

            if form.has_changed() and form.is_valid():
                form.save()
                success = True
        elif 'telegram_form' in request.POST:
            form = ProfileTelegramForm(request.POST, instance=request.user)

            if form.has_changed() and form.is_valid():
                user: User = form.save(commit=False)
                user.telegram_user = user.telegram_user.replace('@', '')
                user.telegram_id = None
                user.save(update_fields=('telegram_user', 'telegram_id'))

                success = True
        elif 'telegram_unlink' in request.POST and request.user.telegram_id:
            request.user.telegram_id = None
            request.user.save(update_fields=('telegram_id',))

            messages.info(
                request,
                'Cuenta de Telegram desvinculada correctamente',
            )

        if success:
            messages.success(
                request,
                '¡Perfil actualizado con éxito!',
            )

        return redirect('profile')


class SignUpView(UserPassesTestMixin, MetadataMixin, FormView):

    template_name = 'users/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('profile')

    title = 'Crear Cuenta - DAFI'
    description = 'Crear una cuenta en la Delegación de Estudiantes de Informática'
    image = 'images/favicon.png'

    def test_func(self) -> bool:
        return not self.request.user.is_authenticated

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        user: User = form.save(commit=False)

        user.username = user.email
        # TODO: Create an email confirmation system
        # user.is_active = False
        user.save()

        return super().form_valid(form)


class LoginView(MetadataMixin, auth_views.LoginView):

    title = 'Iniciar Sesión - DAFI'
    description = 'Iniciar sesión en la Delegación de Estudiantes de Informática'
    image = 'images/favicon.png'


class LogoutView(MetadataMixin, auth_views.LogoutView):

    title = 'Cerrar Sesión - DAFI'


class PasswordChangeView(MetadataMixin, auth_views.PasswordChangeView):

    title = 'Cambiar clave - DAFI'


class PasswordChangeDoneView(MetadataMixin, auth_views.PasswordChangeDoneView):

    title = 'Clave cambiada - DAFI'


class PasswordResetView(MetadataMixin, auth_views.PasswordResetView):

    title = 'Recuperar clave - DAFI'
    description = 'Recuperar clave en la Delegación de Estudiantes de Informática'
    image = 'images/favicon.png'


class PasswordResetDoneView(MetadataMixin, auth_views.PasswordResetDoneView):

    title = 'Recuperación de clave enviada - DAFI'


class PasswordResetConfirmView(MetadataMixin, auth_views.PasswordResetConfirmView):

    title = 'Confirmar recuperación de clave - DAFI'


class PasswordResetCompleteView(MetadataMixin, auth_views.PasswordResetCompleteView):

    title = 'Clave recuperada - DAFI'
