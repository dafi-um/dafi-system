from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.tokens import default_token_generator
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    FormView,
    TemplateView,
    View,
)

from djoser import utils
from djoser.email import ActivationEmail
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
        elif 'verify_email' in request.POST and request.user.can_send_verify_email():
            email = ActivationEmail(self.request, {'user': request.user})
            email.send([request.user.email])

            request.user.verify_email_sent = timezone.now()
            request.user.save(update_fields=('verify_email_sent',))

            messages.info(
                request,
                'Se ha enviado un correo de verificación a tu dirección de e-mail',
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
    success_url = reverse_lazy('signup_success')

    title = 'Crear Cuenta - DAFI'
    description = 'Crear una cuenta en la Delegación de Estudiantes de Informática'
    image = 'images/favicon.png'

    def test_func(self) -> bool:
        return not self.request.user.is_authenticated

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        user: User = form.save(commit=False)

        user.username = user.email
        user.is_active = False
        user.save()

        email = ActivationEmail(self.request, {'user': user})
        email.send([user.email])

        return super().form_valid(form)


class SignUpSuccessView(MetadataMixin, TemplateView):

    template_name = 'users/signup_success.html'

    title = 'Cuenta creada - DAFI'
    description = 'Cuenta creada en la Delegación de Estudiantes de Informática'
    image = 'images/favicon.png'


class VerifyEmailView(View):

    def get(self, request: HttpRequest, *args, **kwargs: dict[str, str]) -> HttpResponse:
        try:
            uid = utils.decode_uid(kwargs['uid'])
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return redirect('main:index')

        if not default_token_generator.check_token(user, kwargs['token']):
            return redirect('main:index')

        user.is_active = True
        user.is_verified = True
        user.verify_email_sent = timezone.now()
        user.save(update_fields=('is_active', 'is_verified'))

        return redirect('login')


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
