from django_filters import rest_framework as filters
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтры рецептов."""
    author = filters.CharFilter(field_name='author_id')
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value:
            print(queryset)
            return Recipe.objects.filter(
                favorite_recipe__recipe=self.request.user).all()
        return queryset

    def get_is_in_shopping_cart(self, value, name, obj):
        if value:
            return obj.filter(shopping_recipe__recipe=obj.recipe)
        return obj


class IngredientFilter(filters.FilterSet):
    """Фильтры тегов."""
    ingredient = filters.CharFilter(
        field_name='name',
        lookup_expr='name__istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
