# Generated by Django 4.2.2 on 2023-07-01 23:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_shoppingcartuser_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppingcartuser',
            old_name='shopping_cart',
            new_name='recipe',
        ),
    ]
