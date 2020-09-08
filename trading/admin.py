from django.contrib import admin

from . import models


@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'year', 'quarter')
    list_filter = ['year', 'quarter']


@admin.register(models.TradePeriod)
class TradePeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end')


class TradeOfferLineInline(admin.TabularInline):
    model = models.TradeOfferLine


@admin.register(models.TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ('user', 'creation_date', 'is_visible', 'is_completed')
    list_filter = ['creation_date', 'is_visible', 'is_completed']

    inlines = (TradeOfferLineInline,)


@admin.register(models.TradeOfferAnswer)
class TradeOfferAnswerAdmin(admin.ModelAdmin):
    list_display = ('offer', 'user', 'creation_date', 'is_completed')
    list_filter = ['offer', 'user', 'is_completed']
