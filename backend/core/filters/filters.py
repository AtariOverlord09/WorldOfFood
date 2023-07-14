"""Фильтры для рецептов."""
import django_filters
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

from recipes.models import Recipe

User = get_user_model()


class IngredientFilter(SearchFilter):
    """Фильтр для ингредиентов."""

    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов."""

    author = django_filters.CharFilter(field_name='author__id')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
