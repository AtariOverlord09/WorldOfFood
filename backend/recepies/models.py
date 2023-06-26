"""Модели приложенения recepies."""
from django.core.exceptions import ValidationError
from django.db import models


class Ingridients(models.Model):
    """Модель ингридиентоы."""

    name = models.CharField(max_length=155)
    measurement_unit = models.CharField(max_length=8)


def validate_coocking_time(value):
    if value < 1:
        raise ValidationError('Время приготовления не может быть меньше одной минуты')


class Tags(models.Model):
    name = models.CharField(max_length=155, unique=True)
    color = models.CharField(max_length=155, unique=True)
    slug = models.SlugField(max_length=155, unique=True)


class Recepies(models.Model):
    """Модель рецепта."""

    ingridients = models.ManyToManyField(
        Ingridients,
        through='IngridientsRecepies',
    )
    tags = models.ManyToManyField(
        Tags,
        through='TagsRecepies',
    )
    image = models.ImageField(
        upload_to='recepies/images',
        null=True,
        default=None,
    )
    name = models.CharField(max_length=200)
    text = models.TextField()
    coocking_time = models.IntegerField(
        validators=[validate_coocking_time],
    )

    def __str__(self):
        return self.name


class TagsRecepies(models.Model):
    """Промежуточная модель для связи рецептов и тегов."""

    tags = models.ForeignKey('Tags', on_delete=models.SET_NULL)
    recepies = models.ForeignKey('Recepies', on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.tags} - {self.recepies}'


class IngridientsRecepies(models.Model):
    """Промежуточная модель для связи рецептов и ингридиентов."""

    ingridients = models.ForeignKey('Ingridients', on_delete=models.SET_NULL)
    recepies = models.ForeignKey('Recepies', on_delete=models.SET_NULL)
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.ingridients} - {self.amount}'
