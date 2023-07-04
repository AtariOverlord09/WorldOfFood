"""Модель User."""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Follow(models.Model):
    """Модель подписки."""

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
        return f"{self.follower} подписан на {self.following}"
