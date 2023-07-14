"""Разрешения для доступа к объектам."""
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешения для контроля доступа к изменению/удалению объектов."""

    message = 'Изменять или удалять объекты может только автор'

    def has_object_permission(self, request, view, obj):
        """
        Проверка для изменения/удаления объекетов.
        Изменять/удалять объекты могут только автор.
        """

        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
        )
