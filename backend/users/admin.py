"""Регистрация модели пользователя в админке."""
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    """Модель пользователя в админкой."""

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
        'is_staff',
        'is_active',
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')

    empty_value_display = '-пусто-'
    ordering = ('date_joined',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
