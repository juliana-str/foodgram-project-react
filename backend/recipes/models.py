from django.db import models

from api.validators import validate_slug, validate_amount
from users.models import User


class Ingredient(models.Model):
    """Модель просмотра, создания и удаления ингридиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Ингридиент'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель для просмотра тегов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        validators=(validate_slug,),
        unique=True,
        verbose_name='Уникальный слаг'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        unique=True,
        verbose_name='Цвет в HEX'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель для просмотра ингредиентов."""
    name = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(validate_amount,)
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        # constraints = [
        #         models.UniqueConstraint(
        #             fields=['recipe', 'ingredient'],
        #             name='unique_ingredients'
        #         )
        # ]


class Recipe(models.Model):
    """Модель просмотра, создания, редактирования и удаления рецептов."""
    name = models.CharField(max_length=200)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        IngredientInRecipe,
        on_delete=models.CASCADE,
        verbose_name = 'Ингредиенты',
        related_name='ingredient_in_recipe'
    )
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    is_favorited = models.BooleanField(null=True)
    is_in_shopping_cart = models.BooleanField(null=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'

    def __str__(self):
        return f'{self.name}, {self.author}'


class Favorite(models.Model):
    """Модель для создания избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Добавил в избранное'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'
    )
    favorite_count = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
