# Generated by Django 3.2 on 2023-08-19 14:15

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscribe',
            name='unique_name_following',
        ),
        migrations.RemoveConstraint(
            model_name='subscribe',
            name='check_following',
        ),
        migrations.RenameField(
            model_name='subscribe',
            old_name='following',
            new_name='author',
        ),
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_name_author'),
        ),
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, user=django.db.models.expressions.F('author')), name='check_author'),
        ),
    ]
