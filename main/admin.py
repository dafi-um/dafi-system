from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from .forms import FlatPageForm
from .models import Config


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):

    list_display = ('key', 'name', 'category')


class PageAdmin(FlatPageAdmin):

    form = FlatPageForm


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, PageAdmin)
