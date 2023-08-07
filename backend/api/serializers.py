from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from rest_framework.fields import CurrentUserDefault

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Tag, Recipe
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


class UserCreateSerializer(serializers.ModelSerializer):
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

    class Meta:
        fields = '__all__'
        required_fields = fields
        model = IngredientInRecipe

    def create(self, validated_data):
        try:
            instance = IngredientInRecipe.objects.create(**validated_data)
            return instance
        except TypeError:
            "Неверный формат записи ингридиентов!"

    def update(self, instance, validated_data):
        ingredient = IngredientInRecipe.objects.get(instance=instance)
        if validated_data:
            ingredient.save()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели тегов."""

    class Meta:
        fields = '__all__'
        required_fields = fields
        model = Tag

    def create(self, validated_data):
        try:
            instance = Tag.objects.create(**validated_data)
            return instance
        except TypeError:
            "Неверный тег!"

    def update(self, instance, validated_data):
        tag = Tag.objects.get(instance=instance)
        if validated_data:
            tag.save()


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""

    class Meta:
        fields = '__all__'
        model = Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    image = Base64ImageField(read_only=True)
    tag = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        fields = '__all__'
        required_fields = fields
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели избранное."""
    favorite_count = serializers.IntegerField()

    class Meta:
        fields = '__all__'
        model = Favorite
