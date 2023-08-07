from django.contrib import admin

from recipes.models import IngredientInRecipe, Ingredient, Recipe, Tag


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):

    def ingredients(self, recipe):
        ingredients = []
        for ingredient in recipe.ingredients.all():
            ingredients.append(ingredient.name)
        return ' '.join(ingredients)

    ingredients.short_description = 'Ingredients'

    list_display = (
        'name',
        'author',
        'tags',
        'ingredients',
        'image',
        'text',
        'cooking_time',
    )
    search_fields = ('name', 'tag')


admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(Tag)
