# НАШЁЛ В ИНТЕРНЕТЕ! бУДЕМ ПЕРЕПИСЫВАТЬ!

# Priject api_yamdb
# data:
# 	python api_yamdb/manage.py import_data --paths static/data/users.csv static/data/category.csv static/data/genre.csv static/data/titles.csv  --models User Category Genre Title
# 	python api_yamdb/manage.py import_data --paths static/data/review.csv static/data/comments.csv  --models Review Comment
# 	python api_yamdb/manage.py import_data --paths static/data/genre_title.csv --tables reviews_title_genre

import csv
import os

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from api_yamdb.settings import BASE_DIR


def read_model(model_name, path):
    model_type = ContentType.objects.filter(model=model_name.lower()).first()
    if not model_type:
        return

    model = model_type.model_class()
    items = []
    path = os.path.join(BASE_DIR, path)
    with open(path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            items.append(model(**row))

        if items:
            model.objects.bulk_create(items)


def read_table(table, path, cursor):
    path = os.path.join(BASE_DIR, path)
    with open(path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames
        fields = ', '.join(header)
        values = ', '.join(['%s' for _ in header])
        for row in reader:
            cursor.execute(
                f"INSERT INTO {table}({fields}) VALUES({values})",
                [row[item] for item in header]
            )


class Command(BaseCommand):
    help = 'Импорт данных'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--paths",
            dest="paths",
            nargs='+',
            help="Список путей к файлам",
            type=str,
        )
        parser.add_argument(
            "--models",
            dest="models",
            nargs='+',
            help="Список названий моделей",
            type=str,
        )
        parser.add_argument(
            "--tables",
            dest="tables",
            nargs='+',
            help="Список названий nf,kbw",
            type=str,
        )

    def handle(self, *args, **options):
        paths = options.get("paths")
        models = options.get("models")
        tables = options.get("tables")

        if not models and not tables or models and tables:
            raise CommandError('Не корректное указание параметров')

        if models and paths:
            if len(models) != len(paths):
                raise CommandError('Количество путей и моделей не совпадает')

            for model_name, path in zip(models, paths):
                read_model(model_name, path)

        elif tables and paths:
            if len(tables) != len(paths):
                raise CommandError('Количество путей и таблиц не совпадает')

            cursor = connection.cursor()
            for table, path in zip(tables, paths):
                read_table(table, path, cursor)
