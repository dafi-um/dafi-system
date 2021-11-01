from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import (
    Committee,
    Degree,
    DocumentMedia,
    Group,
    Meeting,
    PeopleGroup,
    Year,
)


def make_hidden(
        modeladmin: admin.ModelAdmin,
        request: HttpRequest,
        queryset: QuerySet):
    queryset.update(hidden=True)
make_hidden.short_description = 'Ocultar documentos seleccionado/s'


def make_not_hidden(
        modeladmin: admin.ModelAdmin,
        request: HttpRequest,
        queryset: QuerySet):
    queryset.update(hidden=False)
make_not_hidden.short_description = 'Mostrar documentos seleccionado/s'


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):

    list_display = ('name', 'manager')

    autocomplete_fields= ('manager',)


@admin.register(DocumentMedia)
class DocumentMediaAdmin(admin.ModelAdmin):

    list_display = ('name', 'category', 'hidden')
    list_filter = ('hidden',)

    search_fields = ('name', 'category')

    actions = (make_hidden, make_not_hidden)


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):

    list_display = ('name', 'id', 'order', 'is_master')


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):

    list_display = ('year', 'degree', 'telegram_group_link')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):

    list_display = (
        'name', 'get_degree', 'year',
        'delegate', 'subdelegate', 'telegram_group_link'
    )

    autocomplete_fields= ('delegate', 'subdelegate')

    def get_degree(self, obj):
        return obj.year.degree
    get_degree.short_description = 'Titulación'
    get_degree.admin_order_field = 'year__degree'


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):

    list_display = ('date', 'is_ordinary', 'minutes_approved')

    autocomplete_fields= ('documents', 'attendees', 'absents')


class PeopleGroupMemberInline(admin.TabularInline):

    model = PeopleGroup.members.through

    autocomplete_fields= ('user',)


@admin.register(PeopleGroup)
class PeopleGroupAdmin(admin.ModelAdmin):

    list_display = ('name', 'is_hidden', 'show_in_meetings')

    inlines = (PeopleGroupMemberInline,)
