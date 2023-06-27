"""Обработчики приложения api."""
from rest_framework import viewsets
from api.serializers import RecipeCreateSerializer

from recipes.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    """Обработчик для модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
