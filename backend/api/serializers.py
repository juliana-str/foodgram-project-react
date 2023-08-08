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

    def to_representation(self, instance):
        return RecipeGetSerializer(instance).to_representation(instance)


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        read_only=True,
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        amount = validated_data.pop('amount')
        tags = validated_data.pop('tag')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            IngredientInRecipe.objects.create(
                achievement=current_ingredient,
                amount=amount,
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        ingredients_data = validated_data.pop('ingredients')
        lst = []
        for ingredient in ingredients_data:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            lst.append(current_ingredient)
        instance.ingredients.set(lst)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipePostSerializer(instance).to_representation(instance)


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
