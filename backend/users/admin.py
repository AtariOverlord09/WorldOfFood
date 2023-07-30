"""Регистрация модели пользователя в админке."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


class CustomUserAdmin(admin.ModelAdmin):
    """Модель пользователя в админке."""

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')

    empty_value_display = '-пусто-'
    ordering = ('date_joined',)


admin.site.register(User, CustomUserAdmin)
