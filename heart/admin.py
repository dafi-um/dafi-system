from django.contrib import admin

from .models import Subject


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'acronym', 'year', 'quarter')
    list_filter = ['year', 'quarter']


admin.site.register(Subject, SubjectAdmin)
