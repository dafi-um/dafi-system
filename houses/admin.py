from django.contrib import admin

from .models import (
    House,
    HouseProfile,
    PointsTransaction,
)


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):

    list_display = ('name', 'points')

    search_fields = ('name',)


@admin.register(HouseProfile)
class HouseProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'house', 'points')
    list_select_related = ('user', 'house')

    search_fields = ('user', 'house', 'nickname')

    autocomplete_fields = ('user', 'house')


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'house', 'event', 'user', 'points')
    list_select_related = ('user', 'house', 'event')

    search_fields = ('user', 'house', 'event')

    autocomplete_fields = ('user', 'house', 'event')
