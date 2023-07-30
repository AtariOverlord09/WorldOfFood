"""Регистрация модели пользователя в админке."""
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdmin(admin.ModelAdmin):
    """Модель пользователя в админке."""

    def change_user_link(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.username)

    change_user_link.short_description = 'Username'

    list_display = (
        'id',
        'username',
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')

    empty_value_display = '-пусто-'
    ordering = ('date_joined',)


admin.site.register(User, CustomUserAdmin)
