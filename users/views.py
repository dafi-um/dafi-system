from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .forms import ProfileForm, TelegramForm


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.success = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'profile_form' not in context:
            context['profile_form'] = ProfileForm(instance=self.request.user)

        if 'telegram_form' not in context:
            context['telegram_form'] = TelegramForm(instance=self.request.user)

        context['success'] = self.success

        return context

    def post(self, request, **kwargs):
        if 'profile_form' in request.POST:
            form = ProfileForm(request.POST, instance=request.user)

            if form.has_changed() and form.is_valid():
                user = form.save()
                self.success = True
        elif 'telegram_form' in request.POST:
            form = TelegramForm(request.POST, instance=request.user)

            if form.has_changed() and form.is_valid():
                user = form.save(commit=False)
                user.telegram_id = None
                user.save()

                self.success = True
        elif 'telegram_unlink' in request.POST and request.user.telegram_id:
            request.user.telegram_id = None
            request.user.save()

        return super().get(request, **kwargs)
