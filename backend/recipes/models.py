from django.db import models

from .validators import validate_slug
from users.models import User


class Ingredient(models.Model):
    """Модель просмотра, создания и удаления ингридиентов."""
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Ингридиент'
    ),
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    ),

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель для просмотра тегов."""
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
        on_delete=models.CASCADE
    ),
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient')
    )
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    is_favorited = models.BooleanField(null=True)
    is_in_shopping_cart = models.BooleanField(null=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель для просмотра ингредиентов."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

