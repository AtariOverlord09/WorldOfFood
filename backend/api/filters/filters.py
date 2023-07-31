"""Фильтры для рецептов."""
import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Count
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
    tags = django_filters.CharFilter(
        field_name='tags__slug',
        method='filter_by_tags',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_by_tags(self, queryset, name, value):
        """
        Метод фильтрации рецептов по каждому из указанных в запросе тегу.
        Возвращает:
            QuerySet: Набор запросов, содержащий рецепты,
            которые имеют все указанные теги.
        """

        tags = self.request.GET.getlist('tags')

        # Исключаем теги, которые не привязаны ни к одному рецепту
        valid_tags = TagRecipe.objects.filter(slug__in=tags).annotate(
            recipe_count=Count('recipe')
        )
        valid_tags = [tag.slug for tag in valid_tags if tag.recipe_count > 0]

        # Фильтруем рецепты по каждому из указанных тегов
        for tag in valid_tags:
            queryset = queryset.filter(tags__slug=tag)

        return queryset
