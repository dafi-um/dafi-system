from django.contrib import admin

from .models import Subject, Room


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'year', 'quarter')
    list_filter = ['year', 'quarter']


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'members')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Room, RoomAdmin)
