from django.contrib import admin

from . import models


def make_hidden(modeladmin, request, queryset):
    queryset.update(hidden=True)
make_hidden.short_description = 'Ocultar documentos seleccionado/s'

def make_not_hidden(modeladmin, request, queryset):
    queryset.update(hidden=False)
make_not_hidden.short_description = 'Mostrar documentos seleccionado/s'


@admin.register(models.Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager')


@admin.register(models.DocumentMedia)
class DocumentMediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'hidden')
    list_filter = ('hidden',)
    actions = (make_hidden, make_not_hidden)


@admin.register(models.Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ('year', 'course', 'telegram_group_link')


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'course', 'delegate', 'subdelegate', 'telegram_group_link')


@admin.register(models.Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('date', 'is_ordinary', 'minutes_approved')


class PeopleGroupMemberInline(admin.TabularInline):
    model = models.PeopleGroup.members.through


@admin.register(models.PeopleGroup)
class PeopleGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_hidden', 'show_in_meetings')

    inlines = (PeopleGroupMemberInline,)
