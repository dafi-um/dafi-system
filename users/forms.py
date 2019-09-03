from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm

UserModel = get_user_model()


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = UserModel


class ProfileUserForm(forms.ModelForm):
    class Meta():
        model = UserModel
        fields = ('first_name', 'last_name')


class ProfileTelegramForm(forms.ModelForm):
    class Meta():
        model = UserModel
        fields = ('telegram_user',)
