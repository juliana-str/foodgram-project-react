import os
import json
from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def read_ingredients():
    with open(os.path.join(settings.BASE_DIR, 'ingredients.json'),
              'r', encoding='utf-8') as f:
        data = json.load(f)
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
