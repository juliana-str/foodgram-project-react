from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, request
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from django.shortcuts import get_object_or_404

from api.serializers import (
    IngredientSerializer,
    IngredientInRecipeSerializer,
    RecipeSerializer,
    TagSerializer
)
from recipes.models import Recipe, Ingredient, IngredientInRecipe, Tag
from users.permissions import IsAuthorOrReadOnly


class IngredientViewSet(mixins.ListModelMixin, GenericViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated,)

    def get_ingredient(self):
        """Метод получения определенного ингредиента."""
        return get_object_or_404(Ingredient, pk=self.kwargs.get('ingredient_id'))


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)

    def get_tag(self):
        """Метод получения определенного тега."""
        return get_object_or_404(Tag, pk=self.kwargs.get('tag_id'))


class RecipeViewSet(ModelViewSet):
    """Вьюсет для просмотра, создания, изменения, удаления рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_recipe(self):
        """Метод получения определенного рецепта."""
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

    def perform_create(self, serializer):
        """Метод создания рецепта."""
        serializer.save(author=self.request.user)


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    """Вьюсет для создания и удаления рецептов из избранного."""
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Метод получения определенного автора."""
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

    queryset = Recipe.objects.filter(is_favorited=True).all()
    def perform_create(self, serializer):
        """Метод создания подписки на автора."""
        serializer.save(user=self.request.user, recipe=self.get_queryset())


class ShoppingCartViewSet(ModelViewSet):
    """Вьюсет для просмотра, создания, списка продуктов для рецептов."""
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)

    def create_shopping_cart(self):
        """Метод создания списка покупок."""
        shopping_cart = []
        recipes = Recipe.objects.filter(is_in_shopping_cart=True).all()
        for recipe in recipes:
            shopping_cart.append(recipe.get('ingredients'))
        with open('shopping_cart.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(map(str,shopping_cart)))
