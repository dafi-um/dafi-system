from django.contrib import admin

from .models import (
    House,
    HouseProfile,
    PointsTransaction,
    SelectorOption,
    SelectorOptionPoints,
    SelectorQuestion,
    SelectorResult,
    SelectorResultPoints,
)


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):

    list_display = ('name', 'points')

    search_fields = ('name',)

    autocomplete_fields = ('managers',)


@admin.register(HouseProfile)
class HouseProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'house', 'points')
    list_select_related = ('user', 'house')

    search_fields = ('user', 'house', 'nickname')

    autocomplete_fields = ('user', 'house')


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'house', 'activity', 'user', 'points')
    list_select_related = ('user', 'house', 'activity')

    search_fields = ('user', 'house', 'activity')

    autocomplete_fields = ('user', 'house', 'activity')


class SelectorOptionInline(admin.StackedInline):

    model = SelectorOption


@admin.register(SelectorQuestion)
class SelectorQuestionAdmin(admin.ModelAdmin):

    list_display = ('question', 'category')

    search_fields = ('id', 'question', 'category')

    inlines = (SelectorOptionInline,)


class SelectorOptionPointsInline(admin.StackedInline):

    model = SelectorOptionPoints


@admin.register(SelectorOption)
class SelectorOptionAdmin(admin.ModelAdmin):

    list_display = ('text', 'question')
    list_select_related = ('question',)

    search_fields = ('id', 'text', 'question__question')

    autocomplete_fields = ('question',)

    inlines = (SelectorOptionPointsInline,)


class SelectorResultPointsInline(admin.StackedInline):

    model = SelectorResultPoints


@admin.register(SelectorResult)
class SelectorResultAdmin(admin.ModelAdmin):

    list_display = ('user', 'created')
    list_select_related = ('user',)
    list_filter = ('created',)

    search_fields = ('id', 'user__email', 'user__telegram_user')

    autocomplete_fields = ('user',)

    inlines = (SelectorResultPointsInline,)
