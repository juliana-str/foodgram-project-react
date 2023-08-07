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

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель создания и редактирования подписок на авторов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_name_following'),
            models.CheckConstraint(
                check=~Q(user=F('following')),
                name='check_following'
            )
        ]
