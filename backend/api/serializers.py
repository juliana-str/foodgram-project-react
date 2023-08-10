from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from rest_framework.fields import CurrentUserDefault

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Tag, Recipe, Shopping_cart
)
from users.models import Subscribe, User
from .validators import validate_username


class UserGetSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели пользователей. Просмотр."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user
                                            ).exists()
        return False


class UserPostSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели пользователей.
     Создание, изменение, удаление."""
    username = serializers.CharField(
        max_length=150,
        validators=(validate_username,),
    ),
    first_name = serializers.CharField(
        max_length=150,
    ),
    last_name = serializers.CharField(
        max_length=150,
    ),
    email = serializers.EmailField(
        max_length=254,
    )

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        required_fields = fields
        model = User


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели подписок на авторов.."""
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=CurrentUserDefault(),
    )

    def validate_following(self, data):
        """Проверка подписки на самого себя."""
        if self.context['request'].user == data:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!')
        return data

    class Meta:
        fields = '__all__'
        model = Subscribe
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого автора!'
            ),
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели ингридиентов."""

    class Meta:
        fields = '__all__'
        required_fields = fields
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели ингридиентов."""
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    class Meta:
        fields = '__all__'
        required_fields = fields
        model = IngredientInRecipe

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredient')
        amount = validated_data.pop('amount')
        recipe = validated_data.pop('recipe')
        inredient_in_recipe = IngredientInRecipe.objects.create(
            ingredient=ingredient,
            amount=amount,
            recipe=recipe
        )
        return inredient_in_recipe

    def update(self, instance, validated_data):
        ingredient = validated_data.get('ingredient')
        amount = validated_data.get('amount')
        recipe = validated_data.get('recipe')
        ingredient_in_recipe = IngredientInRecipe.objects.get(
            ingredient=ingredient,
            amount=amount,
            recipe=recipe
        )
        if validated_data:
            ingredient_in_recipe.save()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели тегов."""

    class Meta:
        fields = '__all__'
        model = Tag

    def create(self, validated_data):
        name = validated_data.pop('name')
        slug = validated_data.pop('slug')
        color = validated_data.pop('color')
        tag = Tag.objects.create(name=name,
                                 slug=slug,
                                 color=color)
        return tag

    def update(self, instance, validated_data):
        tag = Tag.objects.get(instance=instance)
        if validated_data:
            tag.save()


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        fields = '__all__'
        model = Recipe

    def to_representation(self, instance):
        return RecipeGetSerializer(instance).to_representation(instance)


class RecipePostUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        fields = (
                'name',
                'author',
                'tags',
                'ingredients',
                'image',
                'text',
                'cooking_time'
        )
        required_fields = fields
        model = Recipe

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError('Нужно добавить ингредиент!')
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tag.set(*tags)
        ingredients_recipe = [
            IngredientInRecipe.objects.create(
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
                recipe=recipe
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.pop('name', instance.name)
        instance.image = validated_data.pop('image', instance.image)
        instance.text = validated_data.pop('text', instance.text)
        instance.cooking_time = validated_data.pop(
            'cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tag.set(*tags)
        ingredients_recipe = [
            IngredientInRecipe.objects.create(
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
                recipe=instance
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_recipe)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipePostUpdateSerializer(instance).to_representation(instance)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели избранное."""
    favorite_count = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Favorite

    def get_favorite_count(self):
        if self.context.get('favorite_count'):
            return Favorite.objects.filter(
                self.context.get('favorite_count')).count()


class Shopping_cartSerializer(serializers.ModelSerializer):
    """Сериалайзер для списка покупок."""
    ingredients_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('ingredients_in_shopping_cart')
        model = Shopping_cart

    def get_ingredients_in_shopping_cart(self):
        shopping_cart = IngredientInRecipe.objects.select_related(
            'recipe', 'ingredient'
        )
        return shopping_cart
