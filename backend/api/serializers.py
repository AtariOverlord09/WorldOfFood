import base64

import webcolors
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from recipes.models import (
    Recipe,
    Ingredient,
    IngredientRecipe,
    Tag,
)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.Serializer):
    """Сериализатор рецепта."""
    pass


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:
        model = Recipe
        fields = '__all__'

        read_only_fields = ('author', )

    def create(self, validated_data):

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            ingredient_id = ingredient.pop('id', None)
            amount = ingredient.pop('amount', None)

            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient_id,
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=amount,
            )

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )

        if (
            'ingredients' not in validated_data
            and 'tags' not in validated_data
        ):
            instance.save()
            return instance

        ingredients_data = []
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            for ingredient in ingredients:
                current_ingredient, status = Ingredient.objects.get_or_create(
                    **ingredient
                )
                ingredients_data.append(current_ingredient)
        tags_data = []
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            for tag in tags:
                current_tag, status = Tag.objects.get_or_create(
                    **tag
                )
                tags_data.append(current_tag)

        instance.ingredients.set(ingredients_data) # заменяем присвоение на set()
        instance.tags.set(tags_data) # заменяем присвоение на set()
        instance.save()

        return instance

    def to_representation(self, value):
        pass
