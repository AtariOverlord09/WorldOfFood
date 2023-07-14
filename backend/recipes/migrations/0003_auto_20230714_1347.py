"""Миграция данных для модели Ingredient."""
import csv

from django.db import migrations


def import_data(apps, schema_editor):
    """Метод для импорта данных из csv файла."""

    Ingredient = apps.get_model('recipes', 'Ingredient')
    with open('../data/ingredients.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            name, measurement_unit = row[0], row[1]
            obj = Ingredient(
                name=name,
                measurement_unit=measurement_unit,
            )
            obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0002_alter_ingredientrecipe_ingredient_and_more"),
    ]

    operations = [
        migrations.RunPython(import_data),
    ]
