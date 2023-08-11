from django.contrib import admin

from recipes.models import (
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
    search_fields = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'tags',
        'ingredients',
        'image',
        'text',
        'cooking_time',
    )
    search_fields = ('name', 'author', 'tags')

    def ingredients(self, recipe):
        ingredients = []
        for ingredient in recipe.ingredients.all():
            ingredients.append(ingredient.name)
        return ' '.join(ingredients)

    def tags(self, recipe):
        tags = []
        for tag in recipe.tags.all():
            tags.append(tag.name)
        return ' '.join(tags)


admin.site.register(IngredientInRecipe)
admin.site.register(Shopping_cart)
