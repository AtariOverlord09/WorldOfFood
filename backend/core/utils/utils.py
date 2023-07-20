"""Общие функции и утилиты."""
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Sum


class ResponseUtil:
    """Утилита для ответа клиенту."""

    @staticmethod
    def errors_processing(model, action):
        """Метод для обработки ошибок."""

        if action == 'add_error':
            error_message = f'Рецепт уже добавлен в {model.__name__}'
        elif action == 'delete_error':
            error_message = f'Рецепт еще не добавлен в {model.__name__}'
        else:
            error_message = 'Неподдерживаемое действие'

        return Response(
            {'error': error_message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @staticmethod
    def get_response(model, action, data=None):
        """
        Метод для формирования ответа на добавление рецепта в список.
        """

        if action == 'add':
            return Response(data, status=status.HTTP_201_CREATED)

        elif action == 'delete':
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return ResponseUtil.errors_processing(
                model,
                action='response_error',
            )


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
