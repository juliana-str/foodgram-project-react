import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def read_ingredients():
    dir = os.path.dirname(settings.BASE_DIR)
    path = os.path.join(dir, 'data', 'ingredients.csv')
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            Ingredient.objects.create(
                name=row[0],
                measurement_unit=row[1],
            )
    print('Данные из файла ingredients.csv загружены')


class Command(BaseCommand):

    def handle(self, *args, **options):
        read_ingredients()
