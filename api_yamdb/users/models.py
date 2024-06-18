from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'


class MyUser(AbstractUser):
    ROLES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z'
            )
        ]
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, default='user', choices=ROLES)
    bio = models.TextField('Биография', blank=True)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
