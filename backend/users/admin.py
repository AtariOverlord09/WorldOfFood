"""Регистрация модели пользователя в админке."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


class CustomUserAdmin(BaseUserAdmin):
    """Модель пользователя в админке."""

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'change_password_link',  # Добавляем колонку для ссылки на смену пароля
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')

    empty_value_display = '-пусто-'
    ordering = ('date_joined',)

    def change_password_link(self, obj):
        # Функция для отображения ссылки на смену пароля
        url = f'/admin/auth/user/{obj.id}/password/'
        return f'<a href="{url}">Изменить пароль</a>'

    change_password_link.allow_tags = True
    change_password_link.short_description = 'Изменить пароль'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
