# Generated by Django 3.2 on 2023-07-31 05:16

from django.db import migrations, models
import api.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230731_0652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveIntegerField(validators=[api.validators.validate_amount], verbose_name='Количество'),
        ),
    ]
