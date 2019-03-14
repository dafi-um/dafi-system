from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib import admin
from django import forms
from django.contrib.flatpages.models import FlatPage

from pagedown.widgets import AdminPagedownWidget


class FlatPageForm(forms.ModelForm):
    content = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = FlatPage
        fields = '__all__'


class PageAdmin(FlatPageAdmin):
    form = FlatPageForm

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, PageAdmin)
