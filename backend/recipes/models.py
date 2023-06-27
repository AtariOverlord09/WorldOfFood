"""Модели приложения recepies."""
from typing import Any
from django.core.exceptions import ValidationError
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(max_length=155, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=8,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError(
            'Время приготовления не может быть меньше одной минуты'
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=155,
        unique=True,
        verbose_name='Название',
    )
    color = models.CharField(max_length=155, unique=True, verbose_name='Цвет')
    slug = models.SlugField(max_length=155, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Теги',
    )
    image = models.ImageField(
        upload_to='recipes/images',
        verbose_name='Изображение',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        validators=[validate_cooking_time],
        verbose_name='Время приготовления (в минутах)',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """Промежуточная модель для связи рецептов и тегов."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        verbose_name='Тег',
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        null=True,
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'{self.tag} - {self.recipe}'


class IngredientRecipe(models.Model):
    """Промежуточная модель для связи рецептов и ингредиентов."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        verbose_name='Ингредиент',
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        verbose_name='Рецепт',
        null=True,
    )
    amount = models.IntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class FavoriteRecipeUser(models.Model):
    """Модель избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        related_name='favorite_recipes',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorite',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCard(models.Model):
    """Модель списка продуктов для покупки."""

    name = models.CharField(max_length=155, verbose_name='название')
    image = models.ImageField(
        upload_to='favorite_recipes/images',
        verbose_name='изображение',
    )
    cooking_time = models.IntegerField(
        validators=[validate_cooking_time],
        verbose_name='Время приготовления (в минутах)',
    )

    class Meta:
        verbose_name = 'Список продуктов'
        verbose_name_plural = 'Списки продуктов'

    def __str__(self):
        return self.name


class ShoppingCardUser(models.Model):
    """Модель для связи рецептов и спикоптов пользователя."""

    user = models.ForeignKey(
        User,
        related_name='shopping_card',
        on_delete=models.CASCADE,
    )
    shopping_card = models.ForeignKey(
        ShoppingCard,
        related_name='users',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список продуктов пользователя'
        verbose_name_plural = 'Списки продуктов пользователей'

    def __str__(self):
        return f'{self.user} - {self.shopping_card}'
