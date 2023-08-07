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
        print(">>>>>>>>")
        print(data[0])

        print(">>>>>>>>")
        # reader = csv.reader(f, delimiter=',')
        # for row in reader:
        for i in range(len(data)):
            Ingredient.objects.get_or_create(
                id=i,
                name=data[i].get("name"),
                measurement_unit=data[i].get("measurement_unit")
            )
    print('Данные из файла ingredients.json загружены')


class Command(BaseCommand):

    def handle(self, *args, **options):
        read_ingredients()
