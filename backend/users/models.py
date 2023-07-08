"""Модель User."""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import CheckConstraint, UniqueConstraint

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

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            UniqueConstraint(
                fields=['follower', 'following'],
                name='Валидатор повторной подписки'
            ),
            CheckConstraint(
                name="Валидатор подписки на себя",
                check=~models.Q(follower=models.F('following')),
            ),
        ]
