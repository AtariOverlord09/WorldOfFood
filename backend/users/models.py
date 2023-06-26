"""Модель User."""
from django.core.validators import EmailValidator
from django.contrib.auth.models import (
    AbstractUser
)
from django.db import models


class User(AbstractUser):
    """Модель пользователя с некоторым переопредлением."""

    fisrt_name = models.CharField(
        max_length=150,
        verbose_name="имя",
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="фамилия",
    )
    email = models.EmailField(
        max_length=254,
        verbose_name="почта",
        validators=[
            EmailValidator(message="Введите верный адрес электронной почты"),
        ],
    )

    def __str__(self):
        return self.username
