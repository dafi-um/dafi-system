from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from .forms import CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('telegramId', 'telegramUser', 'firstYear')}),
    )


admin.site.register(User, CustomUserAdmin)
