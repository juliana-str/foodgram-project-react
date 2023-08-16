from django.contrib import admin

from recipes.models import (
    Favorite,
    IngredientInRecipe,
    Ingredient,
    Recipe,
    Tag,
    Shopping_cart
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('^name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
            'pk', 'name', 'author', 'favorite_count',
            'name', 'cooking_time', 'text', 'tags',
            'image', 'author'
    )
    readonly_fields = ('favorite_count',)
    list_filter = ('name', 'author', 'tags')

    # def ingredients(self, recipe):
    #     ingredients = []
    #     for ingredient in recipe.ingredients.all():
    #         ingredients.append(ingredient.name)
    #     return ' '.join(ingredients)
    #
    # def tags(self, recipe):
    #     tags = []
    #     for tag in recipe.tags.all():
    #         tags.append(tag.name)
    #     return ' '.join(tags)

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        return obj.favorite_recipe.count()

admin.site.register(IngredientInRecipe)
admin.site.register(Shopping_cart)
