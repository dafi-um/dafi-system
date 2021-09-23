from django.contrib import admin
from django.db.models import TextField

from pagedown.widgets import AdminPagedownWidget

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


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):

    list_display = ('title', 'start', 'end', 'club', 'organiser', 'is_public')

    formfield_overrides = {
        TextField: {
            'widget': AdminPagedownWidget
        }
    }


@admin.register(ActivityRegistration)
class ActivityRegistrationAdmin(admin.ModelAdmin):

    list_display = ('activity', 'user', 'is_paid')


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):

    list_display = ('title', 'slug', 'register_start', 'voting_start')

    prepopulated_fields = {'slug': ('title',)}


@admin.register(PollDesign)
class PollDesignAdmin(admin.ModelAdmin):

    list_display = ('title', 'user', 'poll')
