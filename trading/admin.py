from django.contrib import admin

from .models import TradePeriod, TradeOffer, TradeOfferLine


class TradePeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end')


class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ('user', 'pub_date')
    list_filter = ['user', 'pub_date']


class TradeOfferLineAdmin(admin.ModelAdmin):
    list_display = ('offer', 'year', 'subjects', 'curr_group', 'wanted_groups')
    list_filter = ['offer', 'year', 'curr_group', 'wanted_groups']


admin.site.register(TradePeriod, TradePeriodAdmin)
admin.site.register(TradeOffer, TradeOfferAdmin)
admin.site.register(TradeOfferLine, TradeOfferLineAdmin)
