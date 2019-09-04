from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import ProfileUserForm, ProfileTelegramForm, SignUpForm


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

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


class SignUpView(UserPassesTestMixin, FormView):
    template_name = 'users/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('profile')

    def test_func(self):
        return not self.request.user.is_authenticated

    def form_valid(self, form: SignUpForm):
        user = form.save(commit=False)

        user.username = user.email
        # TODO: Create an email confirmation system
        # user.is_active = False
        user.save()

        return super().form_valid(form)
