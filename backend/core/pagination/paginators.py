"""Пацинация для рецептов."""
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация на 6 рецептов на страницу."""

    page_size_query_param = 'limit'
    page_size = 6
