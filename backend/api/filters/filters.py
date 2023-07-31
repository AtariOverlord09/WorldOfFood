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
    """
    Мощный фильтр для рецептов на основе тегов.

    Атрибуты:
        tags (django_filters.CharFilter): Фильтр рецептов по тегам.

    Meta:
        model (Recipe): Модель для рецептов.
        fields (tuple): Поля, доступные для фильтрации, включая теги и авторов.

    Итак, приготовьте свои вкусовые рецепторы,
    и пусть начнется поиск вашего идеального рецепта!
    """

    tags = django_filters.CharFilter(
        field_name='tags__slug',
        method='filter_by_tags',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_by_tags(self, queryset, name, value):
        """
        Метод фильтрации по каждому из указанных в запросе тегу.
        Возвращает:
            QuerySet: Набор запросов, освященный выбранными тегами,
            свободный от дубликатов и готовый служить вашим желаниям.
        """

        tags = self.request.GET.getlist('tags')
        tag_filters = Q()

        for tag in tags:
            tag_filters |= Q(tags__slug=tag)

        return queryset.filter(tag_filters)
