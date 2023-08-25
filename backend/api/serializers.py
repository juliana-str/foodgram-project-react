from django.db import transaction
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Tag,
    Recipe,
    ShoppingCart
)
from users.models import Subscribe, User


class UserGetSerializer(UserCreateSerializer):
    """Сериалайзер для модели пользователей, просмотр."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )
        model = User

    def get_is_subscribed(self, obj):
        return (obj.is_authenticated
                and Subscribe.objects.filter(author=obj).exists()
                )


class UserPostSerializer(UserCreateSerializer):
    """Сериалайзер для модели пользователей, создание, изменение, удаление."""

    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        model = User


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериалайзер для списка авторов на которых подписан пользователь."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscribe.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeMinifiedSerializer(
            recipes, many=True, read_only=True)
        return serializer.data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели подписок на авторов.."""

    class Meta:
        fields = '__all__'
        model = Subscribe
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора!'
            ),
        )

    def validate_author(self, data):
        """Проверка подписки на самого себя."""
        if self.context['request'].user == data:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!')
        return data

    def to_representation(self, instance):
        instance = instance['author']
        return SubscriptionsSerializer(instance, context=self.context).data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели ингридиентов."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Список ингредиентов с количеством для рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер модели ингридиентов для создания рецепта."""
    id = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

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


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    author = UserGetSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='recipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(recipe=obj).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели рецептов."""
    author = UserGetSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def validate_ingredients(self, data):
        if len(data) < 1:
            raise serializers.ValidationError('Нужно добавить ингредиент!')
        for i in range(len(data)-1):
            if not Ingredient.objects.filter(id=data[i]['id']).exists():
                raise serializers.ValidationError(
                    'Нужно выбрать ингредиент из представленных!')
            if data[i] in data[i + 1:]:
                raise serializers.ValidationError(
                    'Такой ингредиент уже есть в рецепте!')
        return data

    def validate_amount(self, data):
        if data < 1:
            raise serializers.ValidationError(
                'Количество продукта должно быть больше 0')
        return data

    def validate_cooking_time(self, data):
        if data < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 1 минуты')
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data,
                                       author=self.context['request'].user)
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
            IngredientInRecipe.objects.bulk_create(
                [IngredientInRecipe(
                    recipe=instance,
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    amount=ingredient['amount']
                ) for ingredient in ingredients]
            )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецепта без ингридиентов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели избранное."""

    class Meta:
        fields = ('user', 'recipe')
        model = Favorite
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили этот рецепт в избранное!'
            ),
        )

    def to_representation(self, instance):
        print(instance)
        instance = instance['recipe']
        return RecipeMinifiedSerializer(instance, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер для списка покупок."""
    ingredients_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('ingredients_in_shopping_cart', 'user', 'recipe')
        model = ShoppingCart

    def get_ingredients_in_shopping_cart(self):
        shopping_cart = IngredientInRecipe.objects.select_related(
            'recipe', 'ingredient'
        )
        return shopping_cart

    def validate_recipe(self, data):
        if ShoppingCart.objects.filter(recipe=data).exists():
            raise serializers.ValidationError('Рецепт уже в корзине.')
        return data

    def to_representation(self, instance):
        instance = instance['recipe']
        return RecipeMinifiedSerializer(instance).data
