from django.contrib import admin

from . import models


@admin.register(models.Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager')


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


class PeopleGroupMemberInline(admin.TabularInline):
    model = models.PeopleGroup.members.through


@admin.register(models.PeopleGroup)
class PeopleGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_hidden', 'show_in_meetings')

    inlines = (PeopleGroupMemberInline,)
