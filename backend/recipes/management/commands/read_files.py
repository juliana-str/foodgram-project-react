import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient



def read_ingredients():
    with open(
            os.path.join(
            settings.BASE_DIR,
            'data', 'ingredients.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            Ingredient.objects.get_or_create(
                id=row[0],
                name=row[1],
                measurement_unit=row[2],
            )
    print('Данные из файла ingredients.csv загружены')


class Command(BaseCommand):

    def handle(self, *args, **options):
        read_ingredients()

