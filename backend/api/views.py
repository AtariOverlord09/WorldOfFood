from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipesWriteSerializer,
    TagsSerializer,
)
from recipes.models import (
    FavoriteRecipeUser,
    Ingredient,
    Recipe,
    ShoppingCartUser,
    TagRecipe,
)


User = get_user_model()


class RecipesViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return FavoriteSerializer
        return RecipesWriteSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        author = self.request.user
        if self.request.GET.get('is_favorited'):
            favorite_recipes_ids = FavoriteRecipeUser.objects.filter(
                user=author,
            ).values('recipe_id')

            return queryset.filter(pk__in=favorite_recipes_ids)

        if self.request.GET.get('is_in_shopping_cart'):
            cart_recipes_ids = ShoppingCartUser.objects.filter(
                user=author,
            ).values('recipe_id')
            return queryset.filter(pk__in=cart_recipes_ids)

        return queryset

    def add_in_list(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': f'Рецепт уже добавлен в {model.__name__}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipe = get_object_or_404(Recipe, pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeListSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_in_list(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': f'Рецепт не добавлен в {model.__name__}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_in_list(FavoriteRecipeUser, request.user, pk)
        return self.delete_in_list(FavoriteRecipeUser, request.user, pk)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_in_list(ShoppingCartUser, request.user, pk)
        return self.delete_in_list(ShoppingCartUser, request.user, pk)

    @action(
        methods=('GET', ),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):

        ingredients = request.user.shopping_carts.values(
            'recipe_id__ingr_in_recipe__ingredient__name',
            'recipe_id__ingr_in_recipe__ingredient__measurement_unit',
        ).annotate(amount=Sum('recipe_id__ingr_in_recipe__amount'))

        ingr_count = ingredients.count()
        shopping_list = [
            '{}) {} - {} ({})\n'.format(
                numerate,
                ingr['recipe_id__ingr_in_recipe__ingredient__name'],
                ingr['amount'],
                ingr[
                    'recipe_id__ingr_in_recipe__ingredient__measurement_unit'
                ]
            )
            for numerate, ingr in enumerate(ingredients, 1)
        ]

        shopping_list.insert(0, f'Количество ингедиентов: {ingr_count}\nСписок ингедиентов:\n\n')
        content = '\n'.join(shopping_list)

        response = HttpResponse(content,  content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; '
            f'filename="{self.request.user.username} shopping list.txt"'
        )

        return response


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TagRecipe.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод ингредиентов"""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class FollowUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.user.follower.filter(following=author).exists():
            return Response(
                {'errors': 'Подписка уже оформлена'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FollowSerializer(
            request.user.follower.create(following=author),
            context={'request': request},
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.user.follower.filter(following=author).exists():
            request.user.follower.filter(following=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'В списке подписок нет такого автора'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubscriptionsView(ListAPIView):
    serializer_class = FollowSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.follower.all()
