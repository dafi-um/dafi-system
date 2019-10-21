from django.contrib import admin

from . import models


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'delegate', 'subdelegate', 'telegram_group_link')


@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'year', 'quarter')
    list_filter = ['year', 'quarter']


@admin.register(models.Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'groups', 'subgroups')


@admin.register(models.Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('date',)


@admin.register(models.DocumentMedia)
class DocumentMediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'hidden')
    list_filter = ('hidden',)
