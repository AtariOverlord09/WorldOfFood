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


class Follow(models.Model):
    """Модель подпадения."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="подписчик",

    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="автор",
    )

    def __str__(self):
        return f"{self.user} подпадает на {self.following}"
