from django.contrib import admin

from .models import TradePeriod, TradeOffer, TradeOfferLine


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


admin.site.register(TradePeriod, TradePeriodAdmin)
admin.site.register(TradeOffer, TradeOfferAdmin)
admin.site.register(TradeOfferLine, TradeOfferLineAdmin)
