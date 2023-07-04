"""Обработчики приложения api."""
from rest_framework import viewsets
from api.serializers import RecipeCreateSerializer
from rest_framework.permissions import IsAuthenticated

from recipes.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    """Обработчик для модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = []

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
