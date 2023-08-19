from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтры рецептов."""
    author = filters.CharFilter(field_name='recipe__author')
    tags = filters.MultipleChoiceFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
