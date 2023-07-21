"""Общие функции и утилиты."""
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from core.exceptions.exceptions import AddingError, DeleteError


def add_or_delete_in_list(
        search_model,
        model,
        user,
        pk,
        request_method,
        serializer,
):
    """
    Метод для добавления рецепта в список (избранное или список продуктов).
    """

    obj_queryset = model.objects.filter(
        user=user,
        recipe__id=pk,
    )

    if request_method == 'POST':
        if obj_queryset:
            raise AddingError(
                expression=model.__name__,
                message='Объект уже существует.',
            )

        recipe = get_object_or_404(search_model, pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = serializer(recipe)

        return serializer.data

    num_deleted, _ = obj_queryset.delete()
    if num_deleted == 0:
        raise DeleteError(
            expression=model.__name__,
            message='Объект ещё не добавлен.',
        )

    return None


def get_response(search_model, model, user, pk, method, serializer):

    try:
        obj_data = add_or_delete_in_list(
            search_model,
            model,
            user,
            pk,
            method,
            serializer,
        )

    except (AddingError, DeleteError) as error:
        return Response(
            {'error': str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if obj_data:
        return Response(
            obj_data,
            status=status.HTTP_201_CREATED,
        )

    return Response(status=status.HTTP_204_NO_CONTENT)


def preparation_shopping_list(request):
    """Метод для подготовки списка продуктов пользователя."""

    ingredients = request.user.shopping_carts.values(
        'recipe_id__ingredients_in_recipe__ingredient__name',
        'recipe_id__ingredients_in_recipe__ingredient__measurement_unit',
    ).annotate(amount=Sum('recipe_id__ingredients_in_recipe__amount'))

    ingredient_count = ingredients.count()
    shopping_list = [
        f'Количество ингедиентов: {ingredient_count}',
        '\nСписок ингедиентов:\n\n',
    ]
    shopping_list += [
        '{number}) {name} - {amount} ({unit})\n'.format(
            number=numerate,
            name=ingredient[
                'recipe_id__ingredients_in_recipe__ingredient__name'
            ],
            amount=ingredient['amount'],
            unit=ingredient[
                'recipe_id__ingredients_in_recipe'
                '__ingredient__measurement_unit'
            ]
        )
        for numerate, ingredient in enumerate(ingredients, 1)
    ]

    return '\n'.join(shopping_list)
