from django.contrib import admin

from . import models


@admin.register(models.DocumentMedia)
class DocumentMediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'hidden')
    list_filter = ('hidden',)


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'course', 'delegate', 'subdelegate', 'telegram_group_link')


@admin.register(models.Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('date',)
