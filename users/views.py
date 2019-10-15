from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from meta.views import MetadataMixin

from .forms import ProfileUserForm, ProfileTelegramForm, SignUpForm


class ProfileView(LoginRequiredMixin, MetadataMixin, TemplateView):
    template_name = 'users/profile.html'

    title = 'Mi Perfil - DAFI'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.success = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'profile_form' not in context:
            context['profile_form'] = ProfileUserForm(instance=self.request.user)

        if 'telegram_form' not in context:
            context['telegram_form'] = ProfileTelegramForm(instance=self.request.user)

        context['success'] = self.success

        return context

    def post(self, request, **kwargs):
        if 'profile_form' in request.POST:
            form = ProfileUserForm(request.POST, instance=request.user)

            if form.has_changed() and form.is_valid():
                user = form.save()
                self.success = True
        elif 'telegram_form' in request.POST:
            form = ProfileTelegramForm(request.POST, instance=request.user)

            if form.has_changed() and form.is_valid():
                user = form.save(commit=False)
                user.telegram_user = user.telegram_user.replace('@', '')
                user.telegram_id = None
                user.save()

                self.success = True
        elif 'telegram_unlink' in request.POST and request.user.telegram_id:
            request.user.telegram_id = None
            request.user.save()

        return super().get(request, **kwargs)


class SignUpView(UserPassesTestMixin, MetadataMixin, FormView):
    template_name = 'users/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('profile')

    title = 'Crear Cuenta - DAFI'
    description = 'Crear una cuenta en la Delegación de Estudiantes de Informática'
    image = 'images/favicon.png'

    def test_func(self):
        return not self.request.user.is_authenticated

    def form_valid(self, form: SignUpForm):
        user = form.save(commit=False)

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
