from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm
from .models import User


class CustomUserAdmin(UserAdmin):

    form = CustomUserChangeForm

    list_display = ('username', 'full_name', 'telegram_user', 'joined', 'is_verified')

    list_filter = UserAdmin.list_filter + ('is_verified',) # type: ignore

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': (
            'is_verified', 'verify_email_sent', 'telegram_id', 'telegram_user', 'first_year'
        )}),
    ) # type: ignore

    @admin.display(ordering='first_name', description='Nombre completo')
    def full_name(self, obj: User) -> str:
        return f'{obj.first_name} {obj.last_name}' if obj.first_name else obj.username

    @admin.display(ordering='date_joined', description='Fecha de alta')
    def joined(self, obj: User) -> str:
        return obj.date_joined.strftime('%d %b %Y %H:%M:%S')


admin.site.register(User, CustomUserAdmin)
