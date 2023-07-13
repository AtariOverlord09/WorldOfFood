from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
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
    class Meta:
        model = TagRecipe
        fields = '__all__'
        read_only_fields = (
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество должно быть больше 1'
            )
        return value


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField(read_only=True)
    measurement_unit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'amount', 'measurement_unit')
        model = IngredientRecipe

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipesReadSerializer(serializers.ModelSerializer):
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

    def get_image(self, obj):
        return obj.image.url

    def get_ingredients(self, obj):
        return RecipeIngredientReadSerializer(
            obj.ingredients_in_recipe.all(),
            many=True,
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return FavoriteRecipeUser.objects.filter(
            recipe=obj,
            user=request.user,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCartUser.objects.filter(
            recipe=obj,
            user=request.user,
        ).exists()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        is_following = Follow.objects.filter(
            follower=request.user,
            following=obj.author,
        ).exists()

        return is_following


class RecipesWriteSerializer(serializers.ModelSerializer):
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
        serializer = RecipesReadSerializer(instance, context=self.context)
        return serializer.data

    def add_ingredients(self, recipe, ingredients):
        for ingr in ingredients:
            ingredient_id = ingr.get('id')
            amount = ingr.get('amount')
            ingredient_recipe, created = IngredientRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient_id=ingredient_id,
                defaults={'amount': amount}
            )
            if not created:
                ingredient_recipe.amount = amount
                ingredient_recipe.save()

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')

        if not ingredients:
            raise ValidationError('Необходим хотя бы 1 ингредиент')
        unique_ingredients = []
        for ingredient in ingredients:
            ingr_id = ingredient['id']
            if ingr_id not in unique_ingredients:
                unique_ingredients.append(ingr_id)
            else:
                raise ValidationError('Повторный ингредиент недопустим')
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise ValidationError('Время приготовления должно быть больше 0')
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        author = serializers.CurrentUserDefault()(self)
        new_recipe = Recipe.objects.create(
            author=author,
            **validated_data,
        )
        new_recipe.tags.set(tags)
        self.add_ingredients(new_recipe, ingredients)

        return new_recipe

    def update(self, recipe, validated_data):
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time',
            recipe.cooking_time,
        )

        recipe.ingredients_in_recipe.all().delete()
        ingredients = validated_data.pop('ingredients')
        with transaction.atomic():
            self.add_ingredients(recipe, ingredients)

        recipe.tags.set(validated_data.get('tags', recipe.tags.all()))

        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipeUser
        fields = ('id',)


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(serializers.ModelSerializer):
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
        return obj.follower.follower.filter(following=obj.following).exists()

    def get_recipes(self, obj):
        queryset = obj.following.recipes.all().order_by('-pub_date')
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            try:
                queryset = queryset[: int(limit)]
            except ValueError:
                raise ValueError('Неверно задан параметр количества рецептов')
        return FollowRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.following.recipes.all().count()
