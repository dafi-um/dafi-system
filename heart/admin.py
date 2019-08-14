from django.contrib import admin

from .models import Year, Subject, Room


class YearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'groups', 'subgroups')


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'year', 'quarter')
    list_filter = ['year', 'quarter']


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'members')


admin.site.register(Year, YearAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Room, RoomAdmin)
