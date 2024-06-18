from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Category, Genre, Title, TitleGenre, Review, Comment
from users.models import MyUser

TABLES = {
    MyUser: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    TitleGenre: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        n = 0
        for models, file_name in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{file_name}',
                'r',
                encoding='utf-8'
            ) as file:
                reader = DictReader(file)
                data = []
                for line in reader:
                    if models == Title:
                        line['category_id'] = line.pop('category')
                    if models == Review or models == Comment:
                        line['author_id'] = line.pop('author')
                    data.append(models(**line))
                models.objects.bulk_create(data)
            self.stdout.write(self.style.WARNING(
                f'Импорт данных из {file_name}...')
            )
            n += 1
        if n == len(TABLES):
            self.stdout.write(self.style.SUCCESS(
                'Импорт из CSV файлов успешно завершён.')
            )
