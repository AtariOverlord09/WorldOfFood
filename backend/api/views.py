"""Обработчики приложения api."""
from django.contrib.auth import get_user_model
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

from core.filters.filters import IngredientFilter, RecipeFilter
from core.pagination.paginators import CustomPagination
from core.permissions.permissions import IsAuthorOrReadOnly
from core.utils.utils import ResponseUtil, preparation_shopping_list
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
    """Вьюсет для обработки запросов к рецептам."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """Метод опредления сериализатора в зависимости от запроса."""

        if self.action in ('favorite', 'shopping_cart'):
            return FavoriteSerializer
        return RecipesWriteSerializer

    def get_queryset(self):
        """Метод для получения списка рецептов."""

        queryset = Recipe.objects.all()
        author = self.request.user
        if self.request.GET.get('is_favorited'):
            return Recipe.objects.filter(
                in_favorite__user=author.id,
            )

        if self.request.GET.get('is_in_shopping_cart'):
            return Recipe.objects.filter(
                recipes_in_shopping_cart__user=author,
            )

        return queryset

    def add_in_list(self, model, user, pk):
        """
        Метод для добавления рецепта в список (избранное или список продуктов).
        """

        response = ResponseUtil()

        if model.objects.filter(user=user, recipe__id=pk).exists():
            return response.errors_processing(
                model=model,
                action='add_error',
            )

        recipe = get_object_or_404(Recipe, pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeListSerializer(recipe)

        return response.get_response(
            data=serializer.data,
            model=model,
            action='add',
        )

    def delete_in_list(self, model, user, pk):
        """
        Метод для удаления рецепта из списка (избранное или список продуктов).
        """

        response = ResponseUtil()

        obj_queryset = model.objects.filter(
            user=user,
            recipe__id=pk,
        )
        num_deleted = obj_queryset.delete()[0]

        if num_deleted == 0:
            return response.errors_processing(
                model=model,
                action='delete_error',
            )
        return response.get_response(model, action='delete')

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """
        Метод для добавления или удаления рецепта в избранное.
        """

        if request.method == 'POST':
            return self.add_in_list(FavoriteRecipeUser, request.user, pk)
        return self.delete_in_list(FavoriteRecipeUser, request.user, pk)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """
        Метод для добавления или удаления рецепта в список продуктов.
        """

        if request.method == 'POST':
            return self.add_in_list(ShoppingCartUser, request.user, pk)
        return self.delete_in_list(ShoppingCartUser, request.user, pk)

    @action(
        methods=('GET', ),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """
        Метод для скачивания списка продуктов в виде текстового файла.
        """

        shopping_list = preparation_shopping_list(request=request)

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; '
            f'filename="{self.request.user.username} shopping list.txt"'
        )

        return response


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для просмотра тегов рецептов.
    """

    queryset = TagRecipe.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для просмотра ингредиентов.
    """

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class FollowUserView(APIView):
    """
    Представление для подписки на автора.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        """
        Метод для подписки на автора.
        """

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
        """
        Метод для отмены подписки на автора.
        """

        author = get_object_or_404(User, id=id)
        if request.user.follower.filter(following=author).delete()[0] > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'В списке подписок нет такого автора'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubscriptionsView(ListAPIView):
    """
    Представление для просмотра списка подписок.
    """

    serializer_class = FollowSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.follower.all()
