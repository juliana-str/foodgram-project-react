from django.db import models
from django.contrib.auth.models import AbstractUser

from recipes.validators import validate_username


class User(AbstractUser):
    """Модель просмотра, создания и удаления пользователей."""
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(validate_username,),
        verbose_name='Уникальный юзернейм'
    ),
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    ),
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    ),
    email = models.EmailField(
        max_length=254,
        verbose_name='Адрес электронной почты'
    ),
    is_subscribed = models.BooleanField()

    def __str__(self):
        return self.username
