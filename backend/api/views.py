from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
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
    permission_classes = (AllowAny,)

    def get_ingredient(self):
        """Метод получения определенного ингредиента."""
        return get_object_or_404(Ingredient, pk=self.kwargs.get('ingredient_id'))


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

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


class ShoppingCartViewSet(ModelViewSet):
    """Вьюсет для просмотра, создания, списка продуктов для рецептов."""
    serializer_class = IngredientInRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_recipe_ingredients(self):
        """Метод получения ингредиентов определенного рецепта."""
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        return recipe.filter('ingredients').all()
