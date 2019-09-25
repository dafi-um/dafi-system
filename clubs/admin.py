from django.contrib import admin

from .models import Club, ClubMeeting


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

    prepopulated_fields = {'slug': ('name',)}


class ClubMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'place', 'moment')
    list_filter = ['club', 'place','moment']


admin.site.register(Club, ClubAdmin)
admin.site.register(ClubMeeting, ClubMeetingAdmin)
