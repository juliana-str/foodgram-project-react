from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтры рецептов."""
    author = filters.CharFilter(field_name='author_id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipe=value).all()
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_recipe=value)
        return queryset


class IngredientFilter(filters.FilterSet):
    """Фильтры тегов."""
    ingredient = filters.CharFilter(
        field_name='name',
        lookup_expr='name__istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
