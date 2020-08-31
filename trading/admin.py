from django.contrib import admin

from . import models


@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'year', 'quarter')
    list_filter = ['year', 'quarter']


@admin.register(models.Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'groups', 'subgroups')


@admin.register(models.TradePeriod)
class TradePeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end')


@admin.register(models.TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ('user', 'creation_date', 'is_visible', 'is_completed')
    list_filter = ['user', 'creation_date', 'is_visible', 'is_completed']


@admin.register(models.TradeOfferLine)
class TradeOfferLineAdmin(admin.ModelAdmin):
    list_display = ('offer', 'year', 'curr_group', 'wanted_groups')
    list_filter = ['offer', 'year', 'curr_group', 'wanted_groups']

@admin.register(models.TradeOfferAnswer)
class TradeOfferAnswerAdmin(admin.ModelAdmin):
    list_display = ('offer', 'user', 'creation_date', 'is_completed')
    list_filter = ['offer', 'user', 'is_completed']
