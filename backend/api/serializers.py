from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from djoser.serializers import (
    UserSerializer,
    UserCreateSerializer,
    PasswordSerializer
)
from requests import Response
from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from rest_framework.fields import CurrentUserDefault

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Tag, Recipe, Shopping_cart
)
from users.models import Subscribe, User
from .validators import validate_username, validate_ingredients


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user
                                            ).exists()
        return False

    class Meta:
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )
        model = User


class UserGetSerializer(UserCreateSerializer):
    """Сериалайзер для модели пользователей, просмотр."""

    class Meta:
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )
        model = User


class UserPostSerializer(UserCreateSerializer):
    """Сериалайзер для модели пользователей, создание, изменение, удаление."""
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
    password = serializers.CharField(
        max_length=150
    )

    class Meta:
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'password'
                  )
        model = User


class SubscribeSerializer(serializers.ModelSerializer):
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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        default=1
    )

    class Meta:
        fields = ('id', 'amount')
        required_fields = fields
        model = IngredientInRecipe

    @transaction.atomic
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

    @transaction.atomic
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

    @transaction.atomic
    def create(self, validated_data):
        name = validated_data.pop('name')
        slug = validated_data.pop('slug')
        color = validated_data.pop('color')
        tag = Tag.objects.create(name=name,
                                 slug=slug,
                                 color=color)
        return tag

    @transaction.atomic
    def update(self, instance, validated_data):
        tag = Tag.objects.get(instance=instance)
        if validated_data:
            tag.save()


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='recipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        return (
                self.context.get('request').user.is_authenticated
                and Favorite.objects.filter(user=self.context['request'].user,
                                            recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
                self.context.get('request').user.is_authenticated
                and Shopping_cart.objects.filter(
            user=self.context['request'].user,
            recipe=obj).exists()
        )

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(
        many=True,
        validators=(validate_ingredients,)
    )
    # tags = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     queryset=Tag.objects.all()
    # )

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    @transaction.atomic
    def create(self, validated_data):
        print('111')
        ingredients = validated_data.pop('ingredients')
        print('22222222')
        tags = validated_data.pop('tags')
        print('33333333333')
        recipe = Recipe.objects.create(**validated_data,
                                       author=self.context['request'].user)
        print('4444444')
        recipe.tags.set(*tags)
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

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(*tags)
        if ingredients is not None:
            instance.ingredients.clear()
            ingredients_recipe = [
                IngredientInRecipe(
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'],
                    recipe=instance
                )
                for ingredient in ingredients
            ]
            IngredientInRecipe.objects.bulk_create(ingredients_recipe)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели избранное."""
    favorite_count = serializers.SerializerMethodField()

    def get_favorite_count(self):
        if self.context.get('favorite_count'):
            return Favorite.objects.filter(
                self.context.get('favorite_count')).count()

    class Meta:
        fields = '__all__'
        model = Favorite
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'favorite_recipe'),
                message='Вы уже добавили этот рецепт в избранное!'
            ),
        )


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
