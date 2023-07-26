from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'tag',
        'name',
        'ingredients',
        'image',
        'text',
        'cooking_time'
    )
    search_fields = ('name', 'tag')


admin.site.register(Ingredient)
admin.site.register(Tag)
