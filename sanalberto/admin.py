from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date')


@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'club', 'organiser')
