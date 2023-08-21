from django_filters import rest_framework as filters
from recipes.models import Favorite, Recipe, ShoppingCart


class RecipeFilter(filters.FilterSet):
    """Фильтры рецептов."""
    author = filters.CharFilter(field_name='recipe__author')
    tags = filters.MultipleChoiceFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.request.user, recipe=obj).all()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            user=self.request.user,
            recipe=obj).all()
