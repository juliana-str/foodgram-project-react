from rest_framework import serializers

from recipes.models import Ingredient, IngredientInRecipe, Tag, Recipe


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


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели тегов."""

    class Meta:
        fields = '__all__'
        required_fields = fields
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""

    class Meta:
        fields = '__all__'
        required_fields = fields
        model = Recipe


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        fields = '__all__'
        model = Recipe






