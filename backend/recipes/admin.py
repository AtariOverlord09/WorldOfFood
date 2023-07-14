"""
Регистрация моделей в админке:
-Рецепты
-Ингедиенты
-Теги
-Избранные рецепты
-Список продуктов
"""
from django.contrib import admin

from recipes.models import (
    FavoriteRecipeUser,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCartUser,
    TagRecipe,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Регистрация в админке модели ингедиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Регистрация в админкой модели рецептов."""

    list_display = (
        'id',
        'name',
        'author',
        'cooking_time',
        'pub_date',
        'get_favorite_count',
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    """Регистрация тегов рецепта в админке."""

    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Регистрация ингредиентов рецепта в админке."""

    list_display = ('ingredient', 'recipe', 'amount')
    search_fields = ('ingredient__name', 'recipe__name')
    list_filter = ('ingredient', 'recipe')


@admin.register(FavoriteRecipeUser)
class FavoriteRecipeUserAdmin(admin.ModelAdmin):
    """Регистрация избранных рецептов в админке."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)


@admin.register(ShoppingCartUser)
class ShoppingCartUserAdmin(admin.ModelAdmin):
    """Регистрация списка продуктов в админке."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
