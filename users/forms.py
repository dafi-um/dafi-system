from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta():
        model = get_user_model()
        fields = ('first_name', 'last_name')


class TelegramForm(forms.ModelForm):
    class Meta():
        model = get_user_model()
        fields = ('telegram_user',)
