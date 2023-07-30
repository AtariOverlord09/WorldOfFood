"""Сериализаторы приложения api."""
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction

from recipes.models import (
    FavoriteRecipeUser,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCartUser,
    TagRecipe,
)
from users.models import Follow
from users.serializers import CustomUserSerializer

User = get_user_model()


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = TagRecipe
        fields = '__all__'
        read_only_fields = (
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """Сериализатор ввода для промежуточной таблицы ингредиентов и рецептов."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    def validate_amount(self, value):
        """
        Метод валидрует количество ингредиентов.
        Он проверяет количество на ненулевое значение.
        """

        if value < 1:
            raise serializers.ValidationError(
                'Количество должно быть больше 1'
            )
        return value


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор вывода для промежуточной
    таблицы ингредиентов и рецептов.
    """

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        fields = ('id', 'name', 'amount', 'measurement_unit')
        model = IngredientRecipe


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор вывода рецептов."""

    tags = TagsSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'name',
            'image',
            'text',
            'id',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
            'is_subscribed',
        )
        read_only_fields = [
            'tags',
            'author',
            'name',
            'image',
            'text',
            'id',
            'ingredients',
            'cooking_time',
        ]

    def get_ingredients(self, obj):
        """Возвращает сериализованные данные ингредиентов рецепта."""

        return RecipeIngredientReadSerializer(
            obj.ingredients_in_recipe.all(),
            many=True,
        ).data

    def get_is_favorited(self, obj):
        """
        Находит и возвращает значение флажка
        добавления рецепта в избранное.
        """

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return FavoriteRecipeUser.objects.filter(
            recipe=obj,
            user=request.user,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Находит и возвращает значение флажка
        добавления рецепта в список продуктов.
        """

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCartUser.objects.filter(
            recipe=obj,
            user=request.user,
        ).exists()

    def get_is_subscribed(self, obj):
        """
        Проверяет подписку пользователя на автора рецепта
        и возвращает значение флажка.
        """

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        is_following = Follow.objects.filter(
            follower=request.user,
            following=obj.author,
        ).exists()

        return is_following


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор ввода рецетов"""

    tags = TagsSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientWriteSerializer(many=True)
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'cooking_time',
        )

    def to_representation(self, instance):
        """Метод для вывода сериализованных данных рецепта."""

        serializer = RecipesReadSerializer(instance, context=self.context)
        return serializer.data

    def _add_ingredients(self, recipe, ingredients):
        """Метод для добавления ингредиентов в рецепт."""

        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_recipe, created = (
                IngredientRecipe.objects.get_or_create(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    defaults={'amount': amount}
                )
            )
            if not created:
                ingredient_recipe.amount = amount
                ingredient_recipe.save()

    def validate_ingredients(self, data):
        """Метод для валидации ингедиентов рецепта."""

        ingredients = self.initial_data.get('ingredients')

        if not ingredients:
            raise ValidationError('Необходим хотя бы 1 ингредиент')

        unique_ingredients = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']

            if ingredient_id in unique_ingredients:
                raise ValidationError('Повторный ингредиент недопустим')
            unique_ingredients.append(ingredient_id)

        return data

    def validate_cooking_time(self, data):
        """Метод для валидации времени приготовления для рецепта."""

        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise ValidationError('Время приготовления должно быть больше 0')
        return data

    def create(self, validated_data):
        """Метод для создания рецепта с ингредиентами и тегами."""

        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        author = serializers.CurrentUserDefault()(self)
        new_recipe = Recipe.objects.create(
            author=author,
            **validated_data,
        )
        new_recipe.tags.set(tags)
        self._add_ingredients(new_recipe, ingredients)

        return new_recipe

    def update(self, recipe, validated_data):
        """Метод обновления рецепта."""

        super().update(recipe, validated_data)

        recipe.ingredients_in_recipe.all().delete()
        ingredients = validated_data.pop('ingredients')

        with transaction.atomic():
            self._add_ingredients(recipe, ingredients)

        tags_data = validated_data.get('tags')
        if tags_data:
            recipe.tags.clear()
            for tag in tags_data:
                recipe.tags.add(tag)

        return recipe


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для промежуточной модели рецептов
    в избранном пользователя.
    """

    class Meta:
        model = FavoriteRecipeUser
        fields = ('id',)


class FollowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов авторов на которых подписан пользователь."""

    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки."""

    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        """
        Проверяет подписан ли пользователь на автора
        и возвращает результат проверки.
        """

        return obj.follower.follower.filter(following=obj.following).exists()

    def get_recipes(self, obj):
        """Возвращает рецепты авторов на которых пописан пользователь."""

        queryset = obj.following.recipes.all().order_by('-pub_date')
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            queryset = queryset[: int(limit)]

        return FollowRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов."""

        return obj.following.recipes.all().count()
