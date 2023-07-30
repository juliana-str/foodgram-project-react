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



