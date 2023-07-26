from django.db import models

from .validators import validate_slug, validate_amount
from users.models import User


class Ingredient(models.Model):
    """Модель просмотра, создания и удаления ингридиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Ингридиент'
    ),
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    ),
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель просмотра, создания и удаления тегов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    ),
    color = models.CharField(
        max_length=7,
        null=True,
        unique=True,
        verbose_name='Цвет в HEX'
    ),
    slug = models.SlugField(
        max_length=200,
        null=True,
        validators=(validate_slug,),
        unique=True,
        verbose_name='Уникальный слаг'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель просмотра, создания, редактирования и удаления рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    ),
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='amount',
        through_fields=('recipe', 'ingredient')
    )
    image = models.ImageField(
        upload_to='recipes/',
    ),
    text = models.TextField(
        verbose_name='Описание'
    ),
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'

    def __str__(self):
        return self.name
