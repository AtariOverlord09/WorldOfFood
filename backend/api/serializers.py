import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from recipes.models import (
    Recipe,
    Ingredient,
    IngredientRecipe,
    Tag,
    FavoriteRecipeUser,
    ShoppingCartUser,
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):

        recipe = self.context.get('recipe')

        ingredient_recipe = IngredientRecipe.objects.filter(
            recipe=recipe,
            ingredient=obj,
        ).first()
        if ingredient_recipe:
            return ingredient_recipe.amount
        return None


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, instance):
        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
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
        self.context['recipe'] = recipe
        recipe.tags.set(tags)

        for ingredient in ingredients:

            ingredient1 = ingredient.pop('ingredient', None)
            amount1 = ingredient.pop('amount', None)

            IngredientRecipe.objects.create(
                ingredient=ingredient1,
                recipe=recipe,
                amount=amount1,
            )

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        self.context['recipe'] = instance

        ingredients_data = validated_data.get('ingredients')
        if ingredients_data:
            instance.ingredients.clear()
            for ingredient in ingredients_data:
                amount = ingredient['amount']
                IngredientRecipe.objects.create(
                    ingredient=ingredient.pop('ingredient'),
                    recipe=instance,
                    amount=amount,
                )

        tags_data = validated_data.get('tags')
        if tags_data:
            instance.tags.set(tags_data)

        instance.save()

        return instance

    def to_representation(self, instance):

        ingredient_serializer = IngredientSerializer(
            instance.ingredients.all(),
            many=True,
            context=self.context,
        )
        ingredients_data = ingredient_serializer.data

        user = self.context.get('user')
        is_favorite = FavoriteRecipeUser.objects.filter(
            user=user,
            recipe=instance,
        ).exists()
        is_in_shopping_cart = ShoppingCartUser.objects.filter(
            user=user,
            recipe=instance,
        ).exists()

        representation = {
            'id': instance.id,
            'tags': TagSerializer(instance.tags.all(), many=True).data,
            'author': UserSerializer(instance.author).data,
            'ingredients': ingredients_data,
            'name': instance.name,
            'text': instance.text,
            'image': instance.image.url,
            'cooking_time': instance.cooking_time,
            'is_favorite': is_favorite,
            'is_in_shopping_cart': is_in_shopping_cart,
        }

        return representation
