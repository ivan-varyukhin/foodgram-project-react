import csv

from django.core.management.base import BaseCommand
from recipes.models import Product, Tag


class Command(BaseCommand):
    help = 'Load ingredients data to DB'

    def handle(self, *args, **options):
        print('Обработка файла tags.csv')
        with open('data/tags.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                name, color, slug = row
                Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug
                )
                count += 1
                print(f'Обработано: {count} записей.')

        print('Обработка файла ingredients.csv')
        with open('data/ingredients.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                name, unit = row
                Product.objects.get_or_create(name=name, measurement_unit=unit)
                count += 1
                if not count % 100:
                    print(f'Обработано: {count} записей.')
        print(f'Всего обработано: {count} записей.')
