from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'date', 'design_register_start',
        'selling_start', 'winner_design'
    )


@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'club', 'organiser')


@admin.register(models.Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'user')
