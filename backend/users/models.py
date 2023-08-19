from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q, F


class User(AbstractUser):
    """Модель просмотра, создания и удаления пользователей."""
    is_subscribed = models.BooleanField(
        null=True
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель создания и редактирования подписок на авторов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_name_author'),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='check_author'
            )
        ]
