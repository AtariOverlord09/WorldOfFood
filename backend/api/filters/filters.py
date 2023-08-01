"""Фильтры для рецептов."""
import django_filters
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, TagRecipe

User = get_user_model()


class IngredientFilter(SearchFilter):
    """Фильтр для ингредиентов."""

    search_param = 'name'

    def filter_queryset(self, request, queryset, view):
        search_value = request.query_params.get(self.search_param)

        if search_value:
            queryset = queryset.filter(name__icontains=search_value)

        return queryset


class RecipeFilter(django_filters.FilterSet):
    """Фильтр рецептов."""

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=TagRecipe.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
