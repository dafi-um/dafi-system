from django import forms


class FiumcraftWhitelistForm(forms.Form):

    nickname = forms.CharField(
        label='Nombre de usuario', max_length=30
    )

    faculty = forms.CharField(
        label='Facultad (si eres de la UM)', max_length=100, required=False
    )

    source = forms.CharField(
        label='¿Cómo nos conociste?', max_length=180
    )
