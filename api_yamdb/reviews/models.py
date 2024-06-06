from django.db import models
from django.contrib.auth.models import AbstractUser


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


class Role(models.Model):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, default=USER)

    def __str__(self):
        return self.name


class MyUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.username


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
    description = models.TextField()
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        related_name='genres'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categories'
    )

    def __str__(self):
        return self.name


class Reviews(models.Model):
    """Модель отзывов."""

    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    score = models.SmallIntegerField('Оценка произведения', choices=CHOICES)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев."""

    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
