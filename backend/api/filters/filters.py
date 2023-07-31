"""Фильтры для рецептов."""
import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.filters import SearchFilter

from recipes.models import Recipe

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
    tags = django_filters.CharFilter(
        field_name='tags__slug',
        method='filter_by_tags',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_by_tags(self, queryset, name, value):
        """Метод фильтрации рецептов по каждому из указанных в запросе тегу."""

        tags_param = self.request.GET.getlist('tags')

        queries = Q()

        for tag in tags_param:
            queries |= Q(tags__slug=tag)

        return queryset.filter(queries)
