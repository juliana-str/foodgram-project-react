import csv
import os

from foodgram_backend import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def read_ingredients():
    path = os.path.join('foodgram-project-react', 'data', 'ingredients.csv')
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            Ingredient.objects.get_or_create(
                name=row[1],
                measurement_unit=row[2],
            )
    print('Данные из файла ingredients.csv загружены')


class Command(BaseCommand):

    def handle(self, *args, **options):
        read_ingredients()

