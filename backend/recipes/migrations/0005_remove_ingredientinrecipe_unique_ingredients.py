# Generated by Django 3.2 on 2023-08-15 07:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_ingredient_options'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredientinrecipe',
            name='unique_ingredients',
        ),
    ]
