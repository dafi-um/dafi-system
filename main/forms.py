from django import forms
from django.contrib.flatpages.models import FlatPage

from pagedown.widgets import AdminPagedownWidget


class FlatPageForm(forms.ModelForm):
    content = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = FlatPage
        fields = '__all__'
