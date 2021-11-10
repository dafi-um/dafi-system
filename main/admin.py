from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from .forms import FlatPageForm
from .models import (
    Config,
    MenuEntry,
)


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):

    list_display = ('key', 'name', 'category')


@admin.register(MenuEntry)
class MenuEntryAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'text', 'internal', 'visible', 'order')
    list_filter = ('internal', 'visible', 'blank')


class PageAdmin(FlatPageAdmin):

    form = FlatPageForm


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, PageAdmin)
