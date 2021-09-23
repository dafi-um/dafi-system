from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm
from .models import User


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('telegram_id', 'telegram_user', 'first_year')}),
    ) # type: ignore


admin.site.register(User, CustomUserAdmin)
