"""Импорт данных из JSON файла."""
import json

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда импорта данных из JSON файла."""

    help = 'Импортировать данные из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к JSON-файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, encoding='utf-8') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Файл не найден.'))
            return
        except json.JSONDecodeError as error:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при чтении JSON-файла: {str(error)}'
            ))
            return

        ingredients_to_create = []
        for ingredient in data:
            ingredients_to_create.append(
                Ingredient(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'],
                )
            )

        try:
            Ingredient.objects.bulk_create(ingredients_to_create)
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно импортированы.'
            ))
        except IntegrityError as error:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при импорте ингредиентов: {str(error)}'
            ))
