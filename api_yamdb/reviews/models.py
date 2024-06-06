from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
    (10, '10'),
)


class Genre(models.Model):
    """Модель жанров."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель жанров."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений."""

    name = models.TextField(max_length=256)
    year = models.IntegerField()
    rating = models.SmallIntegerField('Рейтинг произведения', choices=CHOICES, null=True)
    description = models.TextField(blank=True, default='')
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categories'
    )

    def __str__(self):
        return self.name


class TitleGenre(models.Model):

    title = models.ForeignKey(
        Title,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        related_name='genres'
    )

class Reviews(models.Model):
    """Модель отзывов."""

    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    score = models.SmallIntegerField('Оценка произведения', choices=CHOICES, default=None)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(Reviews,
                               on_delete=models.CASCADE,
                               related_name='reviews',
                               null=True)
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
