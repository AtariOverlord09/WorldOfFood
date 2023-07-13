"""Модели приложения recepies."""
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes.validators import ColorValidator

User = get_user_model()


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


class TagRecipe(models.Model):
    """Промежуточная модель для связи рецептов и тегов."""

    name = models.CharField(
        max_length=155,
        unique=True,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=155,
        unique=True,
        verbose_name='Цвет в HEX формате',
        validators=(ColorValidator(),),
    )
    slug = models.SlugField(max_length=155, unique=True, verbose_name='Slug')

    class Meta:
        ordering = ('name',)
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
    tags = models.ManyToManyField(
        TagRecipe,
        verbose_name='Теги',
    )
    image = models.ImageField(
        upload_to='recipes/images',
        verbose_name='Изображение',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        verbose_name='Время приготовления (в минутах)',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    @property
    def get_favorite_count(self):
        """Считает количество добавлений рецепта в избранное."""

        return FavoriteRecipeUser.objects.filter(recipe=self).count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    """Промежуточная модель для связи рецептов и ингредиентов."""

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='entry_into_recipe',
        on_delete=models.SET_NULL,
        verbose_name='Ингредиент',
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients_in_recipe',
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
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorites',
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCartUser(models.Model):
    """Модель для связи списка продуктов и пользователя."""

    user = models.ForeignKey(
        User,
        related_name='shopping_carts',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipes_in_shopping_cart',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список продуктов пользователя'
        verbose_name_plural = 'Списки продуктов пользователей'

    def __str__(self):
        return f'{self.user} - {self.shopping_card}'
