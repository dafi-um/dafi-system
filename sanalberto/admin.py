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

    list_display = ('title', 'event', 'start', 'end', 'club', 'is_public')
    list_filter = ('event', 'is_public')
    list_select_related = ('event', 'club')

    search_fields = ('title', 'club', 'event')

    autocomplete_fields = ('event', 'club', 'organisers')


@admin.register(ActivityRegistration)
class ActivityRegistrationAdmin(admin.ModelAdmin):

    list_display = ('activity', 'user', 'is_paid')
    list_filter = ('is_paid',)
    list_select_related = ('activity', 'user')

    search_fields = ('id', 'activity__id', 'activity__title', 'user__id', 'user__email')

    autocomplete_fields = ('activity', 'user')


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):

    list_display = ('title', 'slug', 'event', 'register_start', 'voting_start')
    list_filter = ('event',)
    list_select_related = ('event',)

    search_fields = ('title', 'slug', 'event')

    autocomplete_fields = ('winner',)

    prepopulated_fields = {'slug': ('title',)}


@admin.register(PollDesign)
class PollDesignAdmin(admin.ModelAdmin):

    list_display = ('title', 'approved', 'user', 'poll')
    list_select_related = ('poll', 'user')

    search_fields = ('title', 'user', 'poll')

    readonly_fields = ('created',)

    # To change the column name from 'Diseño aprobado' to 'Aprobado' (:
    @admin.display(boolean=True, ordering='is_approved', description='Aprobado')
    def approved(self, obj: PollDesign) -> bool:
        return obj.is_approved


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'poll', 'user')
    list_select_related = ('poll', 'user')

    autocomplete_fields = ('poll', 'user', 'first', 'second', 'third')

    readonly_fields = ('created', 'updated')
