import csv
import os
import json
from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def read_ingredients():
    dir = os.path.dirname(settings.BASE_DIR)
    path = os.path.join(dir, 'data', 'ingredients.json')
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in range(len(data)):
            Ingredient.objects.get_or_create(
                id=i,
                name=data[i].get("name"),
                measurement_unit=data[i].get("measurement_unit")
            )
    print('Данные из файла ingredients.json загружены')

    # dir = os.path.dirname(settings.BASE_DIR)
    # path = os.path.join(dir, 'data', 'ingredients.cvs')
    # with open(path, 'r', encoding='utf-8') as f:
    #     reader = csv.reader(f, delimiter=',')
    #     for row in reader:
    #         if row[0] == 'id':
    #             continue
    #         Ingredient.objects.get_or_create(
    #             id=row[0],
    #             name=row[1],
    #             measurment_unit=row[2]
    #         )
    # print('Данные из файла ingredients.csv загружены')

class Command(BaseCommand):

    def handle(self, *args, **options):
        read_ingredients()
