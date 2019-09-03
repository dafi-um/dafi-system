from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

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


class SignUpForm(UserCreationForm):
    class Meta():
        model = UserModel
        fields = ('email', 'first_name', 'last_name')

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data['email'].endswith('@um.es'):
            self.add_error('email', 'Debe ser una dirección de la UM.')
        else:
            count = UserModel.objects.filter(email=cleaned_data['email']).count()

            if count > 0:
                self.add_error('email', 'Ya existe una cuenta para este e-mail.')

        return cleaned_data
