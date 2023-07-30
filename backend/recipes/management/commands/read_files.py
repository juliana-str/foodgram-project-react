import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from resipes.models import (
    Ingredient, IngredientInRecipe, Tag, Recipe, User
)


def read_users():
    with open(
            os.path.join(
            settings.BASE_DIR,
            'static', 'data', 'ingredients.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            User.objects.get_or_create(
                id=row[0],
                name=row[1],
                measurement_unit=row[2],
            )
    print('Данные из файла ingredients.csv загружены')


def read_category():
    with open(
            os.path.join(
                settings.BASE_DIR,
                'static', 'data', 'category.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            Category.objects.get_or_create(
                id=row[0],
                name=row[1],
                slug=row[2],
            )
    print('Данные из файла category.csv загружены')


def read_genre():
    with open(
            os.path.join(
                settings.BASE_DIR,
                'static', 'data', 'genre.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            Genre.objects.get_or_create(
                id=row[0],
                name=row[1],
                slug=row[2],
            )
    print('Данные из файла genre.csv загружены')


def read_titles():
    with open(
            os.path.join(
                settings.BASE_DIR,
                'static', 'data', 'titles.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            Title.objects.get_or_create(
                id=row[0],
                name=row[1],
                year=row[2],
                category_id=row[3]
            )
    print('Данные из файла titles.csv загружены')


def read_genre_title():
    with open(
            os.path.join(
                settings.BASE_DIR,
                'static', 'data', 'genre_title.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            GenreTitle.objects.get_or_create(
                id=row[0],
                title_id=row[1],
                genre_id=row[2],
            )

    print('Данные из файла genre_title.csv загружены')


def read_review():
    with open(
            os.path.join(
                settings.BASE_DIR,
                'static', 'data', 'review.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            Review.objects.get_or_create(
                id=row[0],
                title_id=row[1],
                text=row[2],
                author_id=row[3],
                score=row[4],
                pub_date=row[5]
            )

    print('Данные из файла review.csv загружены')


def read_comments():
    with open(
            os.path.join(
                settings.BASE_DIR,
                'static', 'data', 'comments.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            Comment.objects.get_or_create(
                id=row[0],
                review_id=row[1],
                text=row[2],
                author_id=row[3],
                pub_date=row[4]
            )
    print('Данные из файла comments.csv загружены')


class Command(BaseCommand):

    def handle(self, *args, **options):
        read_users()
        read_category()
        read_genre()
        read_titles()
        read_genre_title()
        read_review()
        read_comments()
