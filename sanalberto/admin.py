from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date')


@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end', 'club', 'organiser')


@admin.register(models.Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'register_start', 'voting_start')

    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.PollDesign)
class PollDesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'poll')
