from django.contrib import admin

from .models import TradePeriod, TradeOffer, TradeOfferLine, TradeOfferAnswer


@admin.register(TradePeriod)
class TradePeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end')


@admin.register(TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ('user', 'creation_date', 'is_visible', 'is_completed')
    list_filter = ['user', 'creation_date', 'is_visible', 'is_completed']


@admin.register(TradeOfferLine)
class TradeOfferLineAdmin(admin.ModelAdmin):
    list_display = ('offer', 'year', 'curr_group', 'wanted_groups')
    list_filter = ['offer', 'year', 'curr_group', 'wanted_groups']

@admin.register(TradeOfferAnswer)
class TradeOfferAnswerAdmin(admin.ModelAdmin):
    list_display = ('offer', 'user', 'creation_date', 'is_completed')
    list_filter = ['offer', 'user', 'is_completed']
