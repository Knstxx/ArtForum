from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

CHOICES = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)


class Reviews(models.Model):
    """Модель отзывов."""

    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    # title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    score = models.SmallIntegerField('Оценка произведения', choices=CHOICES)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    # title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
