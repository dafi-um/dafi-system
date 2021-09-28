from django.contrib import admin

from .models import (
    Club,
    ClubMeeting,
)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug', 'telegram_group_link')

    prepopulated_fields = {'slug': ('name',)}


@admin.register(ClubMeeting)
class ClubMeetingAdmin(admin.ModelAdmin):

    list_display = ('title', 'club', 'place', 'moment')
    list_filter = ['club', 'place', 'moment']
