# Generated by Django 3.2 on 2023-07-31 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_ingredientinrecipe_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='favorite_count',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
