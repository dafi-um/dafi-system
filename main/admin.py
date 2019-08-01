from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from pagedown.widgets import AdminPagedownWidget

from .forms import FlatPageForm
from .models import Subject


class PageAdmin(FlatPageAdmin):
    form = FlatPageForm


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'acronym', 'year', 'quarter')
    list_filter = ['year', 'quarter']


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, PageAdmin)

admin.site.register(Subject, SubjectAdmin)
