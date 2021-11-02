from django.contrib import admin

from sanalberto.models.polls import PollVote

from .models import (
    Activity,
    ActivityRegistration,
    Event,
    Poll,
    PollDesign,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'date')

    search_fields = ('date',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):

    list_display = ('title', 'event', 'start', 'end', 'public')
    list_filter = ('event', 'is_public')
    list_select_related = ('event', 'club')

    search_fields = ('title', 'id', 'club__name', 'club__id')

    autocomplete_fields = ('event', 'club', 'organisers', 'documents')

    # To change the column name
    @admin.display(boolean=True, ordering='is_public', description='Público')
    def public(self, obj: Activity) -> bool:
        return obj.is_public


@admin.register(ActivityRegistration)
class ActivityRegistrationAdmin(admin.ModelAdmin):

    list_display = ('activity', 'user', 'is_paid')
    list_filter = ('activity__event', 'is_paid')
    list_select_related = ('activity', 'user')

    search_fields = ('id', 'activity__title', 'user__email')

    autocomplete_fields = ('activity', 'user')

    readonly_fields = ('created', 'updated')


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):

    list_display = ('title', 'slug', 'event', 'register_start', 'voting_start')
    list_filter = ('event',)
    list_select_related = ('event',)

    search_fields = ('id', 'title', 'slug')

    autocomplete_fields = ('winner',)

    prepopulated_fields = {'slug': ('title',)}


@admin.register(PollDesign)
class PollDesignAdmin(admin.ModelAdmin):

    list_display = ('title', 'approved', 'user', 'poll', 'created')
    list_select_related = ('poll', 'user')
    list_filter = ('poll__event', 'is_approved')

    search_fields = ('id', 'title', 'user__email', 'poll__title')

    readonly_fields = ('created',)

    # To change the column name
    @admin.display(boolean=True, ordering='is_approved', description='Aprobado')
    def approved(self, obj: PollDesign) -> bool:
        return obj.is_approved


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'poll', 'user', 'updated')
    list_select_related = ('poll', 'user')
    list_filter = ('poll__event', 'created', 'updated')

    search_fields = ('id', 'user__email', 'poll__title')

    autocomplete_fields = ('poll', 'user', 'first', 'second', 'third')

    readonly_fields = ('created', 'updated')
